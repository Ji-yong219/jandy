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
function drop(ev,form){
	ev.preventDefault();
	input_file = form.childNodes[1].childNodes[5];
	info_print = form.childNodes[1].childNodes[3];	

	var files = ev.dataTransfer.files;
	var file = files[0];

	input_file.files = files;

	if (input_file.multiple){
		multiple = true;
	} else{
		multiple = false;
	}

	if (multiple == false){
		size = String(file.size);

		if(size.length<4){size=size+"B";}
		else if(size.length<7){size=Math.round(size/1024) +"KB";}
		else if(size.length<10){size=Math.round(size/1048576)+"MB";}

		info_print.innerHTML = file.name + "<br/>약 " + size +"<br/>클릭하시면 삭제됩니다";

		preview_single_File(file,form);
	}
	else if (multiple == true){
		for(i=0 ; i<files.length ; i++){
			info_print.innerHTML = "파일명 : ";
		}
	}
}
function allow_drop(ev){
	ev.preventDefault();
}
function delete_file(form){
	form.innerHTML = "이곳에 파일을 끌어 놓으세요.";

	form = form.parentNode;

	var preview = form.childNodes[7].childNodes[1].childNodes[2].childNodes[1].childNodes[0];

	var file_input = form.childNodes[5].files;

	if (file_input){
		file_input = "";
		preview.src = "";
	}
}
function preview_single_File(file,form) {
	var preview = form.childNodes[1].childNodes[7].childNodes[1].childNodes[2].childNodes[1].childNodes[0];

	var reader = new FileReader();

	reader.onloadend = function(){
		preview.src = reader.result;
	}

	if (file) {
		reader.readAsDataURL(file);
	}else{
		preview.src = "";
	}
}
