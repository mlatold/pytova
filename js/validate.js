
$().ready(function(){
	$('#content form:not([data-no-validate]) button[type=submit]').click(function() {

		var form = $(this).parents('form');
		
		$('li.error', form).removeClass('error');
		$('span.error-msg', form).html('');
		$('div.error-msg', form).remove();
		$(this).prop('disabled', true);

		$.ajax({
			type: 'POST'
		,	url: form.attr('action')
		,	data: form.serialize() + '&submit=1'
		,	dataType: 'json'
		,	success: function(json) {
				if(json['_success'] == false) {
					$('button[type=submit]:last', form).prop('disabled', false);
					var global_error = language_error('_errors');
					for(var x in json) {
						if(x == '_msg') {
							global_error = json[x];
						}
						else if(x == '_captcha') {
							if(json[x] == false) {
								$('#recaptcha_response_field').parents('li').addClass('error').find('span.error-msg').html(language_error('captcha_wrong'));
							}
							
							if(!$('#captcha:visible').length) {
								$('#captcha').parents('li').show();
								Recaptcha.create(lat['recaptcha_public'], 'captcha', { theme: lat['recaptcha_theme'] });
							}
							else {
								Recaptcha.reload();
							}
						} 
						else if(x.charAt(0) != '_') {
							if(!json[x]['success']) {
								$('#' + x).parents('li').addClass('error');
							}
							$('#' + x).parents('li').find('span.error-msg').html(json[x]['msg']);
						}
					}
					$('footer', form).before('<div class="error-msg">' + global_error + '</div>');
				} else {
					load_page(json);
				}
			}
		});

		return false;
	});

	if($('#captcha:visible').length) {
		Recaptcha.create(lat['recaptcha_public'], 'captcha', { theme: lat['recaptcha_theme'] });
	}
	
	$('#content form:not([data-no-validate]) input').keyup(validate_field).blur(validate_field);
});


function validate_field(field) {
	
	var e = null;
	
	// we got passed an input, probably from an event
	if($(this).is('input')) {
		e = field;
		field = $(this);
	}		

	if(!(field instanceof jQuery)) {
		field = $(field);
	}
	
	var r = { 'success': true, 'msg': '' };

	// match another field
	if(field.data('validate-match') !== undefined && $('#' + field.data('validate-match')).val() != '' && field.val() !== $('#' + field.data('validate-match')).val()) {
		r = { 'success': false, 'msg': language_error('match', field.data('validate-match')) };
	}

	// regex match
	if(field.data('validate-regex') !== undefined) {
		var regex = lat['regex'][field.data('validate-regex')].split('/');
		regex = new RegExp(regex[1], regex[2]);

		if( ! regex.test(field.val())) {
			r = { 'success': false, 'msg': language_error('regex-' + field.data('validate-regex')) };
		}
	}

	// minimum characters
	if(field.data('validate-minlength') !== undefined && field.val().length < field.data('validate-minlength')) {
		r = { 'success': false, 'msg': language_error('minlength', field.data('validate-minlength')) };
	}

	// maximum characters
	if(field.data('validate-maxlength') !== undefined && field.val().length > parseInt(field.data('validate-maxlength').replace(/\D/g,''))) {
		r = { 'success': false, 'msg': language_error('maxlength', field.data('validate-maxlength').replace(/\D/g,'')) };
	}
		
	if(r['success'] == false) {
		clearTimeout(field.data('validate-ajax-timeout'));
		field.parents('li').removeClass('ajaxing').addClass('error').find('span.error-msg').html(r['msg']);
	} 
	else {
		// ajax check field
		if(field.data('validate-ajax') !== undefined) {
			if(field.data('validate-ajax-value') !== field.val()) {
				field.data('validate-ajax-value', field.val()).parents('li').removeClass('error').addClass('ajaxing').find('span.error-msg').html(language_error('_ajax'));
				clearTimeout(field.data('validate-ajax-timeout'));
				field.data('validate-ajax-timeout', setTimeout(function(f) {
					var post_data = { validate: 1 };
					post_data[f.attr('id')] = f.val();
					$.ajax({
						type: 'POST'
					,	url: f.parents('form').attr('action')
					,	data: post_data
					,	dataType: 'json'
					,	success: function(json) {
							if(json[f.attr('id')]['success']) {
								f.parents('li').removeClass('ajaxing error').find('span.error-msg').html(json[field.attr('id')]['msg']);
							}
							else {
								f.parents('li').removeClass('ajaxing').addClass('error').find('span.error-msg').html(json[field.attr('id')]['msg']);
							}
						}
					});
				}, 1000, field));
				return r;
			}			
		}
		else {
			field.parents('li').removeClass('error').find('span.error-msg').html('');
		}
	}
	
	return r;
}

function language_error(name, value) {
	var str = "";

	if(typeof lat['form_language'][name] !== 'undefined') {
		str = lat['form_language'][name];
	}
	
	if(typeof value != 'undefined' && typeof lat['form_language'][name + '-' + value] !== 'undefined') {
		str = lat['form_language'][name + '-' + value];
	}
	else if(value != 'undefined') {
		str = str.replace('%s', value);
	}
	
	return str;
}