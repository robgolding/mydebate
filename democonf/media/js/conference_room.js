connection = true;
voted = false;
timeleft = 0;

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

function refreshData(unread, callback) {
	if (typeof unread == 'undefined') unread = false;
	if (typeof callback == 'undefined') callback = function(){ return false; };
	
	var url = window.location.pathname+"?json"
	if (unread) {
		url += "&unread"
	} else {
		$('#loading').show();
	}
	
	$.getJSON(url, function(data, textStatus){
		
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

function send_message(field) {
	var message = $("input[name='"+field+"']");
	if (!message.val()) {
		$("#input").focus();
		return false;
	}
	
	$('#loading').show();
	$("#input").attr("DISABLED", "disabled");
	$("#submit").attr("DISABLED", "disabled");
	
	var data = "message=" + message.val();
	
	$.post(window.location.pathname,
		{ message: message.val() },
		function(data) {
			$.each(data.messages, function(i, item){
				$("#messages").append("<p><b>"+item['author']+":</b> "+item['content']+"</p>");
			});
			$("#messages-wrapper").animate({ scrollTop: $("#messages").attr("scrollHeight") }, 500);
			$("input[name='"+field+"']").val("");
			$("#input").removeAttr("disabled");
			$("#submit").removeAttr("disabled");
			$("#input").focus();
			$('#loading').hide();
		},
		"json"
	);
	
	return false;
}

function submit_vote() {
	var poll_id = $("input[name='poll_id']").val();
	
	var choice = $(":input[name='choice']:checked");
	
	if (!choice.val()) {
		alert("You need to select a choice.");
		return false;
	}
	
	$.post("/polling/vote/"+poll_id+"/",
		{ choice: choice.val() },
		function(data) {
			$("#vote_div").dialog("close");
			voted = true;
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

function add_intervals()
{
	setInterval(function() {
		t = display_time(timeleft)
		$("#num_members").html("Time left: "+t);
		timeleft--;
		if (timeleft < 0) { timeleft = 0; }
	}, 1000);
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
		//width: $(window).width()*0.9,
		//height: $(window).height()*0.9,
		closeOnEscape: false,
		draggable: false,
		modal: true,
		resizable: false,
		open: function(event, ui) { $(".ui-dialog-titlebar-close").hide(); $('body').css('overflow','hidden');},
		buttons: {
			"Vote": function() { $("#vote-form").submit(); }
		}
	});
}

function add_events()
{
	$("#message-input-form").submit(function() {
		return send_message("message1");
	});
	
	$("#vote-form").submit(function() {
		return submit_vote();
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
	refreshData();
	setInterval("refreshData(true)", 2000);
	
	jQuery.event.add(window, "load", resizeFrame);
	jQuery.event.add(window, "resize", resizeFrame);
	
	add_intervals();
	add_dialogs();
	add_events();
}
