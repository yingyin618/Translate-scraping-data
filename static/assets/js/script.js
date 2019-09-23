var timeVal = 4;
var intervalValue;
var iframeHeight = 100;

function onMyFrameLoad(){
	$(".trans-bar").addClass("d-none");
	$(".progress-bar").removeClass("progress-bar-animated");
	$(".progress-bar").css('width','0');
	$("select[name=s_lang]").val(document.getElementById("trans-container").contentWindow.document.getElementById('langcode').value);
	clearInterval(intervalValue);
	timeVal = 4;
}

$(document).ready(function(){
	iframeHeight = $(window).height()-60;
	$("#submitBtn").click(function(){
		if ($("#s_url").val()==''){
			alert("Please input the url to translate.");
			return false;
		}
		s_url = $("input[name=s_url]").val();
		s_lang = $("select[name=s_lang]").val();
		t_lang = $("select[name=t_lang]").val();
		stext = $("select[name=s_lang]").find('option:selected').text();
		ttext = $("select[name=t_lang]").find('option:selected').text();
		if(! confirm('Are you sure to translate \n`' + s_url +'`\n from ' + stext + ' to ' + ttext)){
			return false;
		}
		$(".trans-bar").removeClass("d-none");
		$(".progress-bar").addClass("progress-bar-animated");
		timeVal = 4;
		intervalValue = setInterval(function(){ 
				timeVal += 2;
				$(".progress-bar").css('width',timeVal + '%');
				if(timeVal == 100) clearInterval(intervalValue);
			},
			3000
		);
		
		iframesrc = window.location.origin + '/translate?s_lang=' + s_lang + '&t_lang=' + t_lang + '&s_url='+encodeURI(s_url);
		iframehtml = '<iframe id="trans-container" onload="onMyFrameLoad(this)" src="' + iframesrc +'" style="height:' + iframeHeight +'px"></iframe>';
		$(".iframe-wrap").html(iframehtml);

	});
});