from django.http import HttpResponse
from django.shortcuts import render
from .myhtmlparser import MyHTMLParser
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Comment
from multiprocessing import Process, Pipe
from langdetect import detect
from langdetect import detect_langs

import boto3
import requests 
import re



translate = boto3.client(
	service_name='translate', 
	region_name='us-west-2', 
	use_ssl=True, 
	aws_access_key_id='AKIAZOOYGAI3L3FP7SWW', 
	aws_secret_access_key='ahAT2ZBxjS/zur3i5A5S6iuc00IwjEejBo/nSYcn'
)
# Create your views here.
def home_view(request,*args, **kwargs):
	return render(request, "home.html", {})

def trans_view(request,*args, **kwargs):

	
	url = request.GET.get("s_url")
	s_lang = request.GET.get("s_lang")
	t_lang = request.GET.get("t_lang")
	parsed_uri = urlparse(url)
	hosturl = '{uri.netloc}/'.format(uri=parsed_uri)
	domainURL = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
	headers = requests.utils.default_headers()
	headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
					'Host': hosturl,
					'Referer': domainURL,
					'Connection': 'keep-alive',
					'Cache-Control': 'max-age=0',
					'Upgrade-Insecure-Requests': '1',
					'Sec-Fetch-Mode': 'navigate',
					'Sec-Fetch-User': '?1',
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
					'Sec-Fetch-Site': 'same-origin',
					'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8,zh-CN;q=0.7,zh;q=0.6',
					'Accept-Encoding': 'gzip, deflate, br'
					})
	try:
		r = requests.get(url, headers)
	except:
		my_context = {
			"results":"<p>Connection is failed.</p> <p>Please confirm your url and try again.</p>"
		}
		return render(request, "message.html", my_context)
	

	soup = BeautifulSoup(r.content, 'html.parser')
	langcode = s_lang
	langindex = 0
	langArr = {}
	# for span in soup.find_all(['span','p','a']):
	# 	if span.string is not None and len(span.string.strip())>3 and re.compile("[\d]+").match(span.string) is None:
	# 		langindex += 1
	# 		if langindex >= 20:
	# 			break
	# 		lang = detect(span.string)
	# 		if langArr.get(lang):
	# 			langArr[lang] += 1
	# 		else:
	# 			langArr[lang] = 1
	# maxlangcnt = 0

	# for (k, v) in langArr.items():
	# 	if maxlangcnt < v:
	# 		maxlangcnt = v
	# 		langcode = k

	# if soup.title is not None:
	# 	htmltitle = soup.title.string
	# 	langcode = detect(htmltitle)

	if str(langcode) == 'zh-cn':
		langcode='zh'
	if(str(langcode).find(s_lang)==-1):
		s_lang = langcode

	if soup.body.get("class"):
		classArray = []
		for eachClass in soup.body['class']:
			classArray.append(eachClass.strip('hidden'))
		soup.body['class'] = classArray
			
	comments = soup.findAll(text=lambda text:isinstance(text, Comment))
	for comment in comments:
		comment.extract()

	for noScript in soup.findAll('noscript'):
		noScript.extract()

	for link_tag in soup.find_all('link'):
		link_tag['href'] = urljoin(url, link_tag['href']) 

	for img_tag in soup.find_all('img'):
		if img_tag.get('src'):
			img_tag['src'] = urljoin(url, img_tag['src'])
		if img_tag.get('data-src'):
			img_tag['data-src'] = urljoin(url, img_tag['data-src'])
			img_tag['src'] = img_tag['data-src']
		if img_tag.get('data-srcset'):
			img_tag['data-srcset'] = ''
		if img_tag.get('srcset'):
			img_tag['srcset'] = ''

	for dom in soup.find_all('a'):
		if dom.string is None:
			for a_child in dom.contents:
				if(str(a_child)==a_child.string):
					a_child.string.wrap(soup.new_tag("span"))
	for dom in soup.find_all('div'):
		if hasattr(dom, 'contents'):
			changeFlag = False
			for subdom in dom.contents:
				if hasattr(subdom, 'contents') is False and subdom.string.strip('\n ')!='':
					changeFlag = True
				
			if changeFlag is True:
				for subdom in dom.find_all():
					subdom.unwrap()
				subdom_content = ''
				for single_content in dom.contents:
					subdom_content += single_content.strip()
				dom.string = subdom_content

	for dom in soup.find_all(['p', 'h1', 'h2', 'h3', 'span']):
		for a_tag in dom.find_all():
			a_tag.unwrap()
		p_content = ''
		for single_content in dom.contents:
			p_content += single_content
		dom.string = p_content
	for script_tag in soup.find_all('script'):
		if script_tag.get('src')!=None:
			script_tag['src'] = urljoin(url, script_tag['src'])
		if script_tag.get('type')=='application/json':
			script_tag.extract()

	preText = ''
	preTextTotal = ''
	textPiece = []
	limitTextLen = 4000
	if langcode=='zh':
		limitTextLen = 2000
	testcnt = 0
	for dom in soup.find_all(True):
		skipFlag = False
		for parent in dom.parents:
			if parent.name in ["script", "pre", "style", "iframe", "code"]:
				skipFlag = True
				break
		if dom.get('placeholder')!=None:
			preText += dom['placeholder'] + "\n(||)\n"
			testcnt += 1
		if dom.string!=None and dom.string == dom.contents[0] and dom.name not in ["script", "style", "iframe", "pre", "code"] and skipFlag == False:
			preText += dom.string.strip() + "\n(||)\n"
			testcnt += 1
			if len(preText) >limitTextLen:
				textPiece.append(preText)
				preText = ''
	
	if preText!='':
		textPiece.append(preText)
		preText = ''
	preTextTotalArr = multiTrans(textPiece, {'s_lang':s_lang, 't_lang': t_lang})
	preTextTotal = preTextTotalArr[0]
	errText = preTextTotalArr[1]

	wordList = re.compile("[\(（]+[\| ]+[\)）]+").split(preTextTotal)

	cnt = 0
	for dom in soup.find_all(True):
		skipFlag = False
		for parent in dom.parents:
			if parent.name in ["script", "pre", "style", "iframe", "code"]:
				skipFlag = True
				break
		if dom.get('placeholder')!=None:
			dom['placeholder'] = wordList[cnt].strip("\n")
			cnt += 1
		if dom.string!=None and dom.string == dom.contents[0] and dom.name not in ["script", "style", "iframe", "pre", "code"] and skipFlag == False:
			if cnt >= len(wordList):
				break
			dom.string = wordList[cnt].strip("\n")
			cnt += 1
	global translate
	my_context = {
		"results":soup.prettify(),
		'langcode':langcode,
		"errorText": errText
	}
	return render(request, "translate.html", my_context)

def transText(source_text, param, conn):
	global translate
	try:
		resultText = translate.translate_text(Text=source_text, SourceLanguageCode=param['s_lang'], TargetLanguageCode=param['t_lang'])
		conn.send([resultText.get('TranslatedText'), ''])
	except:
		errText = "<p>The server encountered a temporary error and could not complete your request.</p><p>Please try again later.</p>"
		conn.send([source_text, errText])
	conn.close()

def multiTrans(param1, param2):
	# create a list to keep all processes
	processes = []

	# create a list to keep connections
	parent_connections = []

	# create a process per instance
	for instance in param1:
		# create a pipe for communication
		parent_conn, child_conn = Pipe()
		parent_connections.append(parent_conn)
		print(parent_conn)
		# create the process, pass instance and connection
		process = Process(target=transText, args=(instance, param2, child_conn))
		processes.append(process)

	# start all processes
	for process in processes:
		process.start()

	# make sure that all processes have finished
	for process in processes:
		process.join()

	total_text = ''
	errorText = ''
	for parent_connection in parent_connections:
		try:
			connData = parent_connection.recv()
			total_text += connData[0]
			if(connData[1]!=''):
				errorText = connData[1]
		except:
			errorText = "<p>The server encountered a temporary error and could not complete your request.</p><p>Please try again later.</p>"

	return [total_text, errorText]