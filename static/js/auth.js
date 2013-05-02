$("#persona_button").click(function(){
	navigator.id.get(persona_login);
	return false;
});

function persona_login(assertion) {
	// got an assertion, now send it up to the server for verification
	if (assertion !== null) {
		$.ajax({
			type: 'POST',
			url: jss['url'] + 'auth/persona',
			data: { assertion: assertion },
			success: function(data) {
				if(data['success'] == true) {
					load_page(data);
				}
				else {
					alert('login failure');
				}
			},
			error: function(res, status, xhr) {
				alert("login failure" + res);
			}
		});
	}
	else {
		//loggedOut();
	}
}