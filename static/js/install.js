function logbox(login_stat){

	if (login_stat == null){
		var login_stat="";
	}

	var login  = document.getElementById("login_form");
	var logout = document.getElementById("logout_form");
	var article = document.getElementById("article");

	if (login_stat.length < 2){
		login.style.display  = '';
		logout.style.display = 'none';
		article.style.display = 'none';
	}
	else {
		login.style.display  = 'none';
		logout.style.display = '';
		article.style.display = 'block';
	}
}