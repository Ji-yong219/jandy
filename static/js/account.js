function account_ok(user_ok){
	
	if (user_ok==null){
		var user_ok="no";
	}
		
	var yes  = document.getElementById("user_ok_yes");
	var no = document.getElementById("user_ok_no");
	if (user_ok=="yes"){
		yes.style.display  = '';
		no.style.display = 'none';
	}
	else {
		yes.style.display  = 'none';
		no.style.display = '';
	}
}
function chk_pw(){
	var chk_pw = document.getElementById("pw").value;
	if (chk_pw.length<6){
		return false;
	}
	else{return  true;}
}
function account_show(){
	document.getElementById("id").innerHTML=user_id;
	document.getElementById("nick").value=user_nick;
	document.getElementById("name").value=user_name;

	if(img!="None"){
		document.getElementById("view_preview").src="static/user_img/"+img;
		//console_log({{url_for('static',filename='/user_img/)}}+img);
	}
}
function chk_account(){
	var pw=document.getElementById("ch_pw").value;
	var pwa=document.getElementById("ch_pwa").value;
	var name=document.getElementById("name").value;
	var nick=document.getElementById("nick").value;

	if(pw.length<6){
		document.getElementById("error").innerHTML='비밀번호를 최소 6자 이상 입력해주세요';
		return false;
	}
	else{
		if(pw==pwa){
			document.getElementById("error").innerHTML='';
			
			if(name==''){
				document.getElementById("error").innerHTML='이름을 입력해 주세요';
				return false;
			}
			else{
				document.getElementById("error").innerHTML='';
				
				if(nick.length<2){
					document.getElementById("error").innerHTML='닉네임을 2자 이상 입력해 주세요';
					return false;
				}
				else{
					document.getElementById("error").innerHTML='';
					return true;
				}
			}
		}
	
		else{
			document.getElementById("error").innerHTML='비밀번호가 일치하지 않습니다';
			return false;
		}
	}
}
