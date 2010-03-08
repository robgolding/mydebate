connection = true;
voted = false;
timeleft = 0;
is_creator = false;
//has_cast_vote = 'undefined';
var room_data_timer_id;
var touch_timer_id;
var vote_data_timer_id;

function connectionLost()
{
	$('#left').block({ 
		message: '<h1>Connection lost...</h1>', 
		css: { padding: '0 10px' } 
    });
}

function connectionRestored()
{
	$('#left').unblock();
	$("#input").focus();
}

$.ajaxSetup({
	error: function(){ if (connection) { connection = false; connectionLost(); } }
});

function touch()
{
	$.getJSON(api_urls['touch'], {room: room_slug}, function(data) { return false; });
}

function end_conference()
{
	return false;
}

function reset()
{
	$.getJSON(api_urls['reset'], {room: room_slug}, function(data) { return false; });
}

function has_voted()
{
	has_cast_vote = false;
	$.ajax({
		url: api_urls['poll_info'],
		data: {room: room_slug},
		success: function(data, textStatus)
			{
				if (data['result'])
				{
					has_cast_vote = data['info']['voted'];
				}
			},
		async: false,
		dataType: 'json'
	});
	
	return has_cast_vote;
}

function begin_vote()
{
	mode = "voting";
	clearInterval(room_data_timer_id);
	touch_timer_id = setInterval(touch, 5000);
	$("#vote_div").dialog('open');
}

function refreshData(unread, callback)
{
	if (typeof unread == 'undefined') unread = false;
	if (typeof callback == 'undefined') callback = function () { return false; };
	
	if (!unread) {
		$('#loading').show();
	}
	
	$.getJSON(api_urls['get_data'], {room: room_slug, unread: unread}, function(data, textStatus){
		
		if (!connection) {
			connection = true;
			connectionRestored();
		}
		
		if (!data['success'])
		{
			jquery_alert("Error", data['error'])
			return false;
		}
		
		timeleft = parseInt(data['time_left']);
		
		is_creator = data['is_creator'];
		
		if (data['current_mode'] == "voting") {
			if (!has_voted())
			{
				begin_vote();
			}
			else
			{
				mode = "waiting";
				clearInterval(room_data_timer_id);
				show_poll_results();
			}
		}
		else if (data['current_mode'] == "conferencing")
		{
			mode = "conferencing";
			$('#left').unblock();
			voted = false;
		}
		
		var messages_html = "";
		$.each(data.messages, function(i, item){
			messages_html = messages_html + "<p><b>"+item['author']+":</b> "+item['content']+"</p>";
		});
		
		if (!unread)
			$("#messages").html(messages_html);
		else
			$("#messages").append(messages_html);
		
		var members_html = "";
		$.each(data.members, function(i, item){
			members_html = members_html + "<p><b>"+item['username']+"</b></p>";
		});
		
		members_html = members_html +  "<p><br /></p><p><b>Mode: </b>"+mode+"</p>";
		
		$("#members").html(members_html);
		
		if (unread)
		{
			if (data['messages'].length > 0)
			{
				$("#messages-wrapper").animate({ scrollTop: $("#messages").attr("scrollHeight") }, 500);
			}
		} else {
			$("#messages-wrapper").attr({ scrollTop: $("#messages").attr("scrollHeight") });
			$('#loading').hide();
			
		}
		
		callback();
	});
}

function send_message(url, slug)
{
	var message = $("input[name='message1']");
	if (!message.val()) {
		$("#input").focus();
		return false;
	}
	
	$('#loading').show();
	$("#input").attr("DISABLED", "disabled");
	$("#submit").attr("DISABLED", "disabled");
	
	data = { room: slug, message: message.val() }
	
	$.post(url, data,
		function(data) {
			
			if (!data['success'])
			{
				jquery_alert("Error", data['error'])
				return false;
			}
			
			$.each(data.messages, function(i, item){
				$("#messages").append("<p><b>"+item['author']+":</b> "+item['content']+"</p>");
			});
			$("#messages-wrapper").animate({ scrollTop: $("#messages").attr("scrollHeight") }, 500);
			$("input[name='message1']").val("");
			$("#input").removeAttr("disabled");
			$("#submit").removeAttr("disabled");
			$("#input").focus();
			$('#loading').hide();
		},
		"json"
	);
	
	return false;
}

function update_graph()
{
	$.getJSON(api_urls['poll_info'], {room: room_slug}, function(data, textStatus) {
		if (!data['success'])
		{
			jquery_alert("Error", data['error'])
			return false;
		}
		
		if (data['info']['num_votes'] < 1)
		{
			clearInterval(poll_data_timer_id);
			jquery_alert("Alert", "Conference creator has reset/ended the conference.", function() { room_data_timer_id = setInterval("refreshData(true)", 2000); });
			$("#results_div").dialog('close');
		}
		graphData = data['results'];
		
		$.plot($("#placeholder"), graphData,
		{
			series: {
				pie: { 
					show: true, 
					pieStrokeLineWidth: 1, 
					pieStrokeColor: '#FFF', 
					//pieChartRadius: 100, 			// by default it calculated by 
					//centerOffsetTop:30,
					//centerOffsetLeft:30, 			// if 'auto' and legend position is "nw" then centerOffsetLeft is equal a width of legend.
					showLabel: true,				//use ".pieLabel div" to format looks of labels
					labelOffsetFactor: 5/6, 		// part of radius (default 5/6)
					//labelOffset: 0        		// offset in pixels if > 0 then labelOffsetFactor is ignored
					label: {
						show: false
					},
					background: { opacity: 0.55 }
				}
			},
			legend: {
				show: true, 
				position: "ne", 
				backgroundOpacity: 0,
				labelFormatter: function(label, series) { return label + " ("+Math.round(series.percent)+'%)'; }
			}
		});
		
		if (data['completed'])
		{
			if (is_creator)
			{
				$("#results_div").dialog('option', 'buttons',
					{
						'End conference': function() { end_conference(); },
						'Go to another period':  function() { reset(); $("#results_div").dialog('close'); clearInterval(poll_data_timer_id); room_data_timer_id = setInterval("refreshData(true)", 2000); }
					}
				);
			}
			else
			{
				$("#results_div").dialog('option', 'buttons',
					{
						'Leave conference': function() { $("#leave-conference").dialog('open'); },
						'Close':  function() { $("#results_div").dialog('close'); clearInterval(poll_data_timer_id); room_data_timer_id = setInterval("refreshData(true)", 2000); }
					}
				);
			}
		}
		else
		{
			$("#results_div").dialog('option', 'buttons', { "Waiting for poll to finish...": function() { return false; } });
		}
	});
}

function show_poll_results()
{
	$("#results_div").dialog('open');
	
	voted = true;
	update_graph();
	poll_data_timer_id = setInterval(update_graph, 2000);
}

function cast_vote()
{
	var poll_id = $("input[name='poll_id']").val();
	
	var choice = $(":input[name='choice']:checked");
	
	if (!choice.val()) {
		jquery_alert("Error", "You need to select a choice.", function() {$("#vote_div").dialog('open');});
		return false;
	}
	
	$.post(api_urls['cast_vote'],
		{ room: room_slug, choice: choice.val() },
		function(data) {
			
			if (!data['result'])
			{
				jquery_alert("Error", data['error']);
			}
			else
			{
				clearInterval(touch_timer_id);
				
				show_poll_results();
			
				/*
				$('#left').block({ 
					message: '<h1>Waiting for poll to complete...</h1>', 
					css: { padding: '0 10px' } 
				});
				*/
			}
		},
		"json"
	);
	
	return false;
}

function resizeFrame() 
{
	var h = $(document).height();
	var w = $(document).width();
	//$("#vote_div").css('height', h);
	//$("#vote_div").css('width',w*0.9);
}

function parse_time(seconds)
{
	seconds = parseInt(seconds);
	
	minutes = parseInt(seconds/60);
	seconds = seconds%60;
	
	if ((minutes+'').length == 1) { minutes = '0' + minutes; }
	if ((seconds+'').length == 1) { seconds = '0' + seconds; }
	
	return minutes+":"+seconds
	
}

function display_time()
{
	t = parse_time(timeleft)
	$("#num_members").html("Time left: "+t);
	timeleft--;
	if (timeleft < 0) { timeleft = 0; }
}
	
function add_intervals()
{
	room_data_timer_id = setInterval("refreshData(true)", 2000);
	setInterval(display_time, 1000);
}

function add_dialogs()
{
	$("#leave-conference").dialog({
		bgiframe: true,
		autoOpen: false,
		width: 470,
		closeOnEscape: false,
		draggable: false,
		modal: true,
		resizable: false,
		buttons: {
			"Yes, I'm sure": function() { window.location = window.location.pathname+"leave/" },
			"No, take me back": function() { $("#leave-conference").dialog('close'); }
		}
	});
	
	$("#vote_div").dialog({
		bgiframe: true,
		autoOpen: false,
		title: "Polling",
		closeOnEscape: false,
		draggable: false,
		modal: true,
		resizable: false,
		open: function(event, ui) { $(".ui-dialog-titlebar-close").hide(); $('body').css('overflow','hidden');},
		buttons: {
			"Vote": function() {
				$("#vote-form").submit();
				$("#vote_div").dialog('close');
			}
		}
	});
	
	$("#results_div").dialog({
		bgiframe: true,
		autoOpen: false,
		title: "Poll Results",
		closeOnEscape: false,
		draggable: false,
		modal: true,
		resizable: false,
		width: 600,
		height: 500,
		open: function(event, ui) { $(".ui-dialog-titlebar-close").hide(); $('body').css('overflow','hidden');},
		buttons: {
				"Waiting for poll to finish...": function() { return false; }
			}
		}
	);
}

function add_events()
{
	$("#message-input-form").submit(function() {
		return send_message(api_urls['send_message'], room_slug);
	});
	
	$("#vote-form").submit(function() {
		return cast_vote();
	});
	
	$("#vote-form input").keypress(function (e) {  
		if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {  
			$("#vote-form").submit();
		}  
	});  
	
	$("#leave-conference-button").click(function(){
		$("#leave-conference").dialog('open');
		return false;
	});
	
	$("#vote-button").click(function(){
		$("#vote_div").dialog('open');
		return false;
	});
}

oldready = ready;

ready = function()
{
	oldready();

	$('#loading').hide();
	$("#input").focus();
	refreshData(false, add_intervals);

	jQuery.event.add(window, "load", resizeFrame);
	jQuery.event.add(window, "resize", resizeFrame);

	add_dialogs();
	add_events();
}
