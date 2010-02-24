connection = true;
voted = false;
timeleft = 0;
//has_cast_vote = 'undefined';

function connectionLost() {
	$('#left').block({ 
		message: '<h1>Connection lost...</h1>', 
		css: { padding: '0 10px' } 
    });
}

function connectionRestored() {
	$('#left').unblock();
	$("#input").focus();
}

$.ajaxSetup({
	error: function(){ if (connection) { connection = false; connectionLost(); } },
});

function has_voted() {
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

function refreshData(url, slug, unread, callback) {
	if (typeof unread == 'undefined') unread = false;
	if (typeof callback == 'undefined') callback = function(){ return false; };
	
	if (!unread) {
		$('#loading').show();
	}
	
	$.getJSON(url, {room: slug, unread: unread}, function(data, textStatus){
		
		if (!connection) {
			connection = true;
			connectionRestored();
		}
		
		if (!unread) $("#messages").html("");
		
		$.each(data.messages, function(i, item){
			$("#messages").append("<p><b>"+item['author']+":</b> "+item['content']+"</p>");
		});
		
		$("#members").html("");
		$.each(data.members, function(i, item){
			$("#members").append("<p><b>"+item['username']+"</b></p>");
		});
		
		if (data['current_mode'] == "voting") {
			if (!voted)
			{
				mode = "voting";
				$("#vote_div").dialog('open');
			}
			else
			{
				mode = "waiting";
			}
		}
		else if (data['current_mode'] == "conferencing")
		{
			mode = "conferencing";
			$('#left').unblock();
			voted = false;
		}
		
		$("#members").append("<p><br /></p><p><b>Mode: </b>"+mode+"</p>");
		
		timeleft = parseInt(data['time_left']);
		
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

function send_message(url, slug) {
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

function update_graph() {
	$.getJSON(api_urls['poll_info'], {room: room_slug}, function(data, textStatus) {
		
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
				labelFormatter: function(label, series) { return label + "("+Math.round(series.percent)+'%)'; }
			}
		});
	});
}

function cast_vote() {
	var poll_id = $("input[name='poll_id']").val();
	
	var choice = $(":input[name='choice']:checked");
	
	if (!choice.val()) {
		alert("You need to select a choice.");
		return false;
	}
	
	$.post(api_urls['cast_vote'],
		{ room: room_slug, choice: choice.val() },
		function(data) {
			
			$("#results_div").dialog('open');
			voted = true;
			
			update_graph();
			
			setInterval(update_graph, 2000);
			
			/*
			$('#left').block({ 
				message: '<h1>Waiting for poll to complete...</h1>', 
				css: { padding: '0 10px' } 
			});
			*/
		},
		"text"
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
		width: 500,
		height: 500,
		open: function(event, ui) { $(".ui-dialog-titlebar-close").hide(); $('body').css('overflow','hidden');},
		buttons: {
			"Close": function() {
				$("#results_div").dialog('close');
			}
		}
	});
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
	refreshData(api_urls['get_data'], room_slug, false);
	setInterval("refreshData(api_urls['get_data'], room_slug, true)", 2000);

	jQuery.event.add(window, "load", resizeFrame);
	jQuery.event.add(window, "resize", resizeFrame);

	add_intervals();
	add_dialogs();
	add_events();
}
