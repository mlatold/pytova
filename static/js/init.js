var js = { loaded: 0, count: 0, code: [], data_buffer: null };

$.ajaxSetup({cache: false});

$().ready(function(){
	//init();

	var offset = new Date().getTimezoneOffset() * -1;
	if(parseInt(offset) != parseInt(jss.time_offset)) {
		jss.time_offset = offset;
		$.post(jss['url'] + 'account/timezone', { json: 1, time_offset: offset });
		$('time').each(function(index) {
			var new_date = '';
			var now = new Date();
			var now_t = now; // tommorow
			var now_y = now; // yesterday
			var date = new Date($(this).data('unix') * 1000);
			now_t.setDate(now_t.getDate() + 1);
			now_y.setDate(now_t.getDate() - 1);

			var time = date.getHours() + ':' + date.getMinutes();
			if(jss['time_24'] == 0) {
				var hours = date.getHours() + 1;
				if(hours > 12) {
					time = (hours - 12) + ':' + ('0' + date.getMinutes()).slice(-2) + 'pm';
				}
				else {
					time = hours + ':' + ('0' + date.getMinutes()).slice(-2) + 'am';
				}
			}

			if(now.getFullYear() == date.getFullYear() && now.getMonth() == date.getMonth() && now.getDate() == date.getDate()) {
				new_date = jss['today'].replace('{time}', time);
			}
			else if(now_y.getFullYear() == date.getFullYear() && now_y.getMonth() == date.getMonth() && now_y.getDate() == date.getDate()) {
				new_date = jss['yesterday'].replace('{time}', time);
			}
			else if(now_t.getFullYear() == date.getFullYear() && now_t.getMonth() == date.getMonth() && now_t.getDate() == date.getDate()) {
				new_date = jss['tommorow'].replace('{time}', time);
			}
			else {
				new_date = date.getFullYear() + '-' + ('0' + date.getMonth()).slice(-2) + '-' + ('0' + date.getDate()).slice(-2) + ' ' + time;
			}

			$(this).html(new_date);
		});
	}

	window.setTimeout(function() {
		$(window).bind('popstate', function(){
			get_page(location.pathname);
		});
	}, 200);
});

/**
 * Initalizes loaded page
 *
 * @param context
 * @returns {Boolean}
 */
 /*
function init(context) {
	if(typeof context == 'undefined') context = null;

	history.replaceState({}, document.title, lat['current_url']);

	if(js['count'] != js['loaded']) {
		return false;
	}

	$('iframe[src="about:blank"]').remove(); // removes recaptcha iframes

	$('a[rel!=external][href^="'+lat_static['url']+'"]', context).on('click', function(e){
		if (typeof window.history.pushState == 'function' && e.button == 0) {
			history.pushState({}, document.title, $(this).attr('href'));
			get_page($(this).attr('href'));
			return false;
		}
		return true;
	});

	$('.close').on('click', function() {
		$(this).off('click');
		$(this).parent().slideUp('fast', function() {
			$(this).remove();
		});
	});

	return true;
}
function ajax_loading(act) {
	// Toggle
	if(typeof act == undefined) {
		if(obj.loading.is(':visible')) {
			act = 'hide';
		} else {
			act = 'show';
		}
	}

	// Close
	if(act == 'hide') {
		obj.loading.fadeOut('fast', function(){
			clearInterval($("#loading").data('interval'));
		});
	}
	// Open
	else if (act == 'show') {
	}
}
*/
/**
 * Loads a new page by ajax
 *
 * @param url
 *//*
function get_page(url) {


	$('#content').after('<div id="loading"></div>');
	var loading = $('#loading');
	var loading_r = 0;

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
			data: { json: 1 },
			success: load_page,
			error: function(jqXHR, textStatus, errorThrown) {
				lat['current_url'] = url;
				load_page({ content: jqXHR.responseText });
				console.log(jqXHR, textStatus, errorThrown);
			},
			dataType: 'json'
		});
	}
	else {
		window.location = url;
	}
}*/

/**
 * Load page contents from ajax response onto the page
 *
 * @param data
 *//*
function load_page(data) {

	// refresh variable array
	if(data['jsv']) {
		lat = data['jsv'];
	}

	if(data['header']) {
		$('header:first *').off();
		$('header:first').html(data['header']);
		init($('header:first'));
	}

	// load content onto the page
	$('html').attr('class', data['classes']);
	$('#content *').off();
	clearInterval($("#loading").data('interval'));
	$('#loading').remove();
	$('#content').html(data['content']);
	$(window).scrollTop(0); // scroll to the top of the page

	// finish up and initalize the page
	init('#content');

	if(data['jsf']) {
		js['count'] = data['jsf'].length;
		js['loaded'] = 0;

		// loads the new javascript files
		$.each(data['jsf'], function(i, v) {
			$.ajax({
				url: v,
				dataType: "script",
				success: function() {
					js['loaded'] = js['loaded'] + 1;
					init('#content');
				},
				error: function(jqXHR, textStatus, errorThrown) {
					console.log(errorThrown);
				}
			});
		});
	} else {
		js['count'] = 0;
		js['loaded'] = 0;
	}
}*/