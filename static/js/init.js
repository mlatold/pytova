var js = { loaded: 0, count: 0, code: [], data_buffer: null };
$.ajaxSetup({cache: false});
var current_url = window.location.href;
var offset = new Date().getTimezoneOffset() * -1;

if(parseInt(offset) != parseInt(jss.time_offset)) {
	$.post(jss['url'] + 'account/timezone', { json: 1, time_offset: offset });
	jss.time_offset = offset; // new detected time offset
	var now = new Date(); //today
	var now_t = now; // tommorow
	now_t.setDate(now_t.getDate() + 1);
	var now_y = now; // yesterday
	now_y.setDate(now_t.getDate() - 1);
	$('time').each(function(index) {
		var date = new Date($(this).data('unix') * 1000);
		// Detect time
		var time = date.getHours() + ':' + date.getMinutes();
		if(jss['time_24'] == 0) {
			var hours = date.getHours();
			if(hours >= 12) {
				time = (hours - 12) + ':' + ('0' + date.getMinutes()).slice(-2) + 'pm';
			}
			else {
				hours = hours == 0 ? 12 : hours;
				time = hours + ':' + ('0' + date.getMinutes()).slice(-2) + 'am';
			}
		}
		// Relative date formats
		if(now.getFullYear() == date.getFullYear() && now.getMonth() == date.getMonth() && now.getDate() == date.getDate()) {
			$(this).html(jss['today'].replace('{time}', time));
		}
		else if(now_y.getFullYear() == date.getFullYear() && now_y.getMonth() == date.getMonth() && now_y.getDate() == date.getDate()) {
			$(this).html(jss['yesterday'].replace('{time}', time));
		}
		else if(now_t.getFullYear() == date.getFullYear() && now_t.getMonth() == date.getMonth() && now_t.getDate() == date.getDate()) {
			$(this).html(jss['tommorow'].replace('{time}', time));
		}
		// Standard date format
		else {
			$(this).html(date.getFullYear() + '-' + ('0' + date.getMonth()).slice(-2) + '-' + ('0' + date.getDate()).slice(-2) + ' ' + time);
		}
	});
}

window.setTimeout(function() {
	$(window).bind('popstate', function(){
		get_page(location.pathname);
	});
}, 200);

init();

/**
 * Initalizes loaded page
 */

function init(context) {
	if(typeof context == 'undefined') context = null;

	// still loading JS!
	if(js['count'] != js['loaded']) {
		return false;
	}

	$("iframe").remove(); // removes iframes created by plugins

	if(context == null || context == '#header') {
		$("#header a:not([href$=#])").click(function() {
			$("#header li").removeClass('on');
			if($(this).parent().attr('id') == "site") {
				$("#header li[data-default]").addClass('on');
			}
			else {
				$(this).parent().addClass('on');
			}
		});

		$("#sign_in a[href$=#]").click(function(){
			navigator.id.get(function(assertion){
				if (assertion !== null) {
					$.post(jss['url'] + 'auth/persona', { assertion: assertion },
						function(data) {
							if(data['success'] == true) {
								load_page(data);
							}
							else {
								alert(data['error']);
							}
						}, "json"
					);
				}
				else {
					window.location = jss['url'] + 'auth/sign_out'
				}
			});
			return false;
		});
	}

	$("a[rel!=external][href^='"+jss['url']+"']", context).not("[href$=#]").on('click', function(e){
		if (typeof window.history.pushState == 'function' && e.button == 0) {
			history.pushState({}, $('html').data('title'), $(this).attr('href'));
			jss['current_url']
			get_page($(this).attr('href'));
			return false;
		}
		return true;
	});
/*
	$('.close').on('click', function() {
		$(this).off('click');
		$(this).parent().slideUp('fast', function() {
			$(this).remove();
		});
	});
*/
	return true;
}

/**
 * Loads a new page by ajax
 *
 * @param url
 */
function get_page(url) {
	$('#content').after('<div id="loading"></div>');
	var loading = $('#loading');
	var loading_r = 0;
	$(window).scrollTop(0); // scroll to the top of the page

	loading.data('interval', setInterval(function(){
		loading_r = (loading_r + 1) % 360;
		loading.css({ WebkitTransform: 'rotate(' + loading_r + 'deg)', '-moz-transform': 'rotate(' + loading_r + 'deg)'});
	}, 5));

	if (typeof window.history.pushState == 'function') {
		//$("#content").css({ opacity: 0.5 });
		//$('body').append('<div id="load"></div>');
		$.ajax({
			type: 'POST',
			url: url,
			data: { fmt: 'json' },
			success: load_page,
			error: function(jqXHR, textStatus, errorThrown) {
				//jss['current_url'] = url;
				load_page({ content: jqXHR.responseText });
				console.log(jqXHR, textStatus, errorThrown);
			},
			dataType: 'json'
		});
	}
	else {
		window.location = url;
	}
}

/**
 * Load page contents from ajax response onto the page
 *
 * @param data
 */
function load_page(data, textStatus, jqXHR) {
	// refresh variable array
	js = data['js'];
	if(typeof data['debug'] != 'undefined') console.log(data['debug'])
	if(typeof data['nav'] == 'undefined') data['nav'] = [];
	document.title = $('html').data('title') + (data['nav'].length ? " :: " + data['nav'][data['nav'].length-1][0] : "");
	history.replaceState({}, document.title, typeof data['url'] != 'undefined' ? data['url'] : window.location.href);

	if(typeof data['header'] != 'undefined') {
		$('#header *').off();
		$('#header').html(data['header']);
		init('#header');
	}

	// load content onto the page
	$('html').attr('classes', data['classes']);
	$('#content *').off();
	clearInterval($("#loading").data('interval'));
	$('#loading').remove();
	$('#content').html(data['out']);

	// finish up and initalize the page
	init('#content');

	if(data['jsf']) {
		js['count'] = data['jsf'].length;
		js['loaded'] = 0;

		// loads the new javascript files
		$.each(data['jsf'], function(i, v) {
			$.getScript(v, function() {
				js['loaded'] = js['loaded'] + 1;
				init('#content');
			});
		});
	} else {
		js['count'] = 0;
		js['loaded'] = 0;
	}
}