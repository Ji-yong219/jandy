function chk_post(){
	var title = document.getElementById("title_input").value;
	var contain = document.getElementById("contain_input").value;

	if (title != '' && contain != ''){
		return true;
	}
	else{
		return false;
	}
}
