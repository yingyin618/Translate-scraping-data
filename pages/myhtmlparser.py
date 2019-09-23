from html.parser import HTMLParser
from html.entities import name2codepoint

class MyHTMLParser(HTMLParser):
	content = []

	def handle_starttag(self, tag, attrs):
		print ("Encountered a start tag:", tag)
		# parsed_uri = urlparse('http://stackoverflow.com/questions/1234567/blah-blah-blah-blah' )
		# result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
		# print(result)

	def handle_data(self, data):
		if data.strip()!="" and len(data.strip()) > 5:
			self.content.append(data.strip())