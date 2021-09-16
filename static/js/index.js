function logbox(session_stat){

	if (session_stat==null){
		var session_stat="";
	}

	var login  = document.getElementById("login_form");
	var logout = document.getElementById("logout_form");
	if (session_stat.length<2){
		login.style.display  = '';
		logout.style.display = 'none';
		document.getElementById("regist").style.display='inline-block';
		document.getElementById("find_account").style.display='inline-block';
	}
	else {
		login.style.display  = 'none';
		logout.style.display = '';
		if(img!="None"){
			document.getElementById("profile").src="static/user_img/"+img;
		}
	}
}

function pw_chk(){
	pw = document.getElementById("pwbox").value;

	if (pw.length>5){
		return true;
	}else{alert('비밀번호는 6자 이상 입력해주세요');return false;}
}

function tick(){
 $('#ticker_01 li:first').slideUp( function () { $(this).appendTo($('#ticker_01')).slideDown(); });
}
setInterval(function(){ tick () }, 3000);

function weatherclick1(){
	document.getElementById("time_weather").style.display="inline-block"
	document.getElementById("more1").style.display="none"
	document.getElementById("more2").style.display="inline-block"
}
function weatherclick2(){
	document.getElementById("time_weather").style.display="none"
	document.getElementById("more1").style.display="inline-block"
	document.getElementById("more2").style.display="none"
}
