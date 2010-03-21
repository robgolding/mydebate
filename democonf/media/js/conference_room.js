
/* a few global variables */

// connection is OK to start with
connection = true;

// user has not voted yet
voted = false;

// timeleft is zero to start
timeleft = 0;

// assume we didn't create this room
is_controller = false;

// variables to hold the timer IDs (important later,
// so we can cancel intervals at will)
var room_data_timer_id;
var touch_timer_id;
var vote_data_timer_id;

function connectionLost()
{
	/* The connection to the server has been lost,
	 so "block" the left pane */
	$('#left').block({ 
		message: '<h1>Connection lost...</h1>', 
		css: { padding: '0 10px' } 
    });
}

function connectionRestored()
{
	/* Connection has been restored, so unblock the left pane
	and place focus into the message box. */
	$('#left').unblock();
	$("#input").focus();
}

function clearAllIntervals()
{
	/* clear all the intervals to stop the requests */
	clearInterval(room_data_timer_id);
	clearInterval(touch_timer_id);
	clearInterval(vote_data_timer_id);
}

$.ajaxSetup({
	/*
	Call the connectionLost() function if an AJAX connection
	ever fails.
	*/
	error: function(){ if (connection) { connection = false; connectionLost(); } }
});

function touch()
{
	/* Directly call the "touch" API operation on the current room,
	to signify that the user is still here. */
	$.getJSON(api_urls['touch'], {room: room_slug}, function(data) { return false; });
}

function leave_conference()
{
	/* Leave the conference (just redirect to the leave/ page for this room) */
	window.location = window.location.pathname+"leave/";
}

function end_conference()
{
	/* End the conference using the "end" operation on the rooms API.
	Only the controller can call this operation. */
	$.getJSON(api_urls['end'], {room: room_slug}, function(data) { 
		if (data['success'])
			window.location = window.location.pathname+"leave/";
		else
			jquery_alert("Error", data['error']);
	});
}

function reset()
{
	/* Reset the conference using the "reset" API operation.
	Only the controller can do this. */
	$.getJSON(api_urls['reset'], {room: room_slug}, function(data) { return false; });
}

function has_voted()
{
	/* Convenience function to *synchronously* ask the server
	if the current user has voted yet (for security). */
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
	/* Begin the voting process.
	Opens the voting window, cancels the message checking interval
	and sets a new one to let the server know we are here every
	5 seconds. */
	mode = "voting";
	clearInterval(room_data_timer_id);
	touch_timer_id = setInterval(touch, 5000);
	$("#vote_div").dialog('open');
}

function scrollToBottom(animate)
{
	/* Scroll to the bottom of the messages pane, with an optional animation. */
	animate = typeof(animate) != 'undefined' ? animate : true;
	
	if (animate)
		$("#messages-wrapper").animate({ scrollTop: $("#messages").attr("scrollHeight") }, 500);
	else
		$("#messages-wrapper").attr({ scrollTop: $("#messages").attr("scrollHeight") });
}

function update_messages(messages, append)
{
	/* Update the messages pane with the given list of messages,
		in overwrite mode by default (i.e. not append mode). */
	
	// default value of append is false
	append = typeof(append) != 'undefined' ? append : false;
	
	// parse the messages into some HTML
	var messages_html = "";
	$.each(messages, function(i, item){
		messages_html = messages_html + "<p><b>"+item['author']+":</b> "+item['content']+"</p>";
	});
	
	if (!append)
		// overwrite the HTMl if append is false
		$("#messages").html(messages_html);
	else
		// append to it otherwise
		$("#messages").append(messages_html);
	
	// scroll if there were any messages
	if (messages.length > 0)
		scrollToBottom();
}

function update_members(members)
{
	/* Update the members pane with the list of members given. */
	var members_html = "";
	$.each(members, function(i, item){
		members_html = members_html + "<p><b>"+item['username']+"</b></p>";
	});
	
	// always overwrite, the list should be short
	$("#members").html(members_html);
}

function refreshData(unread, callback)
{
	/* The main function to refresh all data about the room, and set the countdown
	to the right value. Called every 2 seconds by default. 
	Value of "unread" specifies whether to check for unread messages or *all* messages,
	and callback is called when the AJAX request succeeds. */
	
	// default value of unread is false
	unread = typeof(unread) != 'undefined' ? unread : false;
	
	// default callback function is a function that does nothing
	callback = typeof(callback) != 'undefined' ? callback : function () { return false; };
	
	// the AJAX call itself
	$.getJSON(api_urls['get_data'], {room: room_slug, unread: unread}, function(data, textStatus) {
		
		// if the connection was previously down, restore it
		if (!connection) {
			connection = true;
			connectionRestored();
		}
		
		// if the API operation was *not* successful, output
		// the error + clear all the intervals (leaves conference when OK is clicked)
		if (!data['success'])
		{
			jquery_alert("Error", data['error'], leave_conference)
			clearAllIntervals();
		}
		
		// set the countdown timer to the correct value
		timeleft = parseInt(data['time_left']);
		
		// let the JS know if the room was created by this user
		is_controller = data['is_controller'];
		
		if (data['current_mode'] == "voting") {
			// if we are in voting mode...
			if (!has_voted())
			{
				// and this user has not already voted,
				// then begin the process
				begin_vote();
			}
			else
			{
				// otherwise we are waiting for the others to finish voting
				mode = "waiting";
				
				// so clear the main refreshData interval
				clearInterval(room_data_timer_id);
				
				// and show the results pane
				show_poll_results();
			}
		}
		else if (data['current_mode'] == "conferencing")
		{
			// if we are in conferencing mode, then there's nothing to do really...
			mode = "conferencing";
			
			// we can't have voted though, so this is false
			voted = false;
		}
		
		// update the messages with the server's list (using the unread value as the
		// append argument)
		update_messages(data['messages'], unread);
		
		// update the members list with the server's list of members
		update_members(data['members']);
		
		// call the callback function last
		callback();
	});
}

function send_message(url, slug)
{
	/* Sends the message in the input box and clears the box */
	
	// get the message in the input box
	var message = $("input[name='message1']");
	
	// if the content is empty, then give focus back and return.
	// nothing to do!
	if (!message.val()) {
		$("#input").focus();
		return false;
	}
	
	// disable the input box + submit button
	// (so the user can't accidentally submit twice)
	$("#input").attr("DISABLED", "disabled");
	$("#submit").attr("DISABLED", "disabled");
	
	// construct the post data to give to the API
	data = { room: slug, message: message.val() }
	
	// post the data
	$.post(url, data,
		function(data) {
			// if the request was *not* successfull, pass the error message on
			// and return
			if (!data['success'])
			{
				jquery_alert("Error", data['error'])
				return false;
			}
			
			// otherwise, update the messages list with the returned list
			// from the server (in append mode)
			update_messages(data['messages'], true);
			
			// set the message input field back to empty
			$("input[name='message1']").val("");
			
			// enable the input field and submit button
			$("#input").removeAttr("disabled");
			$("#submit").removeAttr("disabled");
			
			// give focus back to the input field
			$("#input").focus();
		},
		"json"
	);
	
	return false;
}

function update_graph()
{
	/* Update the results graph with the latest poll results */
	$.getJSON(api_urls['poll_info'], {room: room_slug}, function(data, textStatus) {
		if (!data['success'])
		{
			// if the request was not successfull, then we can assume that the debate was ended by the controller
			jquery_alert("Debate ended", "The debate has ended. Click OK to return to the list of debates.", function() {
				// so leave the conference
				leave_conference();
				return false;
			});
		}
		
		if (data['info']['num_votes'] < 1)
		{
			// if there are no votes, then the debate has rolled over to
			// another period
			clearInterval(vote_data_timer_id);
			// so offer a dialog with an OK button that joins the next period
			jquery_alert("Alert", "Conference controller has chosen to go to another period.", function() { room_data_timer_id = setInterval("refreshData(true)", 2000); });
			$("#results_div").dialog('close');
		}
		
		// get the poll results from the server
		graphData = data['results'];
		
		// plot the results using the flot plugin + flot-pie (to make a pie chart)
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
		
		// if the vote has completed, then offer some action buttons:
		if (data['completed'])
		{
			// if this user is the owner of the room
			if (is_controller)
			{
				// then give the choice to end the debate or go to another period
				$("#results_div").dialog('option', 'buttons',
					{
						'End conference': function() { end_conference(); },
						'Go to another period':  function() { reset(); $("#results_div").dialog('close'); clearInterval(vote_data_timer_id); room_data_timer_id = setInterval("refreshData(true)", 2000); }
					}
				);
			}
			else
			{
				// otherwise give the choice to leave or continue
				$("#results_div").dialog('option', 'buttons',
					{
						'Leave conference': function() { $("#leave-conference").dialog('open'); },
						'Close':  function() { $("#results_div").dialog('close'); clearInterval(vote_data_timer_id); room_data_timer_id = setInterval("refreshData(true)", 2000); }
					}
				);
			}
		}
		else
		{
			// if the vote is not finished yet, then place a disabled button stating this
			$("#results_div").dialog('option', 'buttons', { "Waiting for poll to finish...": function() { return false; } });
		}
	});
}

function show_poll_results()
{
	/* Show the poll results */
	
	// open the results dialog
	$("#results_div").dialog('open');
	
	// user has voted
	voted = true;
	
	// update the graph, and set an interval to update it every 2 seconds
	update_graph();
	vote_data_timer_id = setInterval(update_graph, 2000);
}

function cast_vote()
{
	/* cast a vote in the current poll */
	
	// get the choice that the user picked
	var choice = $(":input[name='choice']:checked");
	
	// if there was not choice, then present the error
	if (!choice.val()) {
		jquery_alert("Error", "You need to select a choice.", function() {$("#vote_div").dialog('open');});
		return false;
	}
	
	// post the choice to the API
	$.post(api_urls['cast_vote'],
		{ room: room_slug, choice: choice.val() },
		function(data) {
			
			// if the call failed for some reason, present the error
			if (!data['result'])
			{
				jquery_alert("Error", data['error']);
			}
			else
			{
				// otherwise, clear the "touch" interval, and show the results
				// (which starts up a new interval anyway)
				clearInterval(touch_timer_id);
				
				show_poll_results();
			}
		},
		"json"
	);
	
	return false;
}

function parse_time(seconds)
{
	/* Parse an integer number of seconds into a string, e.g.:
	
		parse_time(75) = 1:15
	
	*/
	seconds = parseInt(seconds);
	
	minutes = parseInt(seconds/60);
	seconds = seconds%60;
	
	if ((minutes+'').length == 1) { minutes = '0' + minutes; }
	if ((seconds+'').length == 1) { seconds = '0' + seconds; }
	
	return minutes+":"+seconds
	
}

function display_time()
{
	/* Display the current countdown time in the counter box */
	t = parse_time(timeleft)
	$("#num_members").html("Time left: "+t);
	
	// decrement the time left (but not below zero)
	timeleft--;
	if (timeleft < 0) { timeleft = 0; }
}
	
function add_intervals()
{
	/* Add all the required intervals (room data and display time) */
	room_data_timer_id = setInterval("refreshData(true)", 2000);
	setInterval(display_time, 1000);
}

function add_dialogs()
{
	/* Setup all the dialogs */
	
	// leave conference dialog (are you sure?)
	$("#leave-conference").dialog({
		bgiframe: true,
		autoOpen: false,
		width: 470,
		closeOnEscape: false,
		draggable: false,
		modal: true,
		resizable: false,
		buttons: {
			"Yes, I'm sure": function() { leave_conference(); },
			"No, take me back": function() { $("#leave-conference").dialog('close'); }
		}
	});
	
	// vote dialog (poll choices)
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
	
	// results dialog (to hold pie chart)
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
	/* Add all the events */
	
	// message input form submit action
	$("#message-input-form").submit(function() {
		return send_message(api_urls['send_message'], room_slug);
	});
	
	// vote form submit action
	$("#vote-form").submit(function() {
		return cast_vote();
	});
	
	// catch the enter button for the voting form
	$("#vote-form input").keypress(function (e) {  
		if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {  
			$("#vote-form").submit();
		}  
	});  
	
	// open the leave conference dialog when the user clicks leave
	$("#leave-conference-button").click(function(){
		$("#leave-conference").dialog('open');
		return false;
	});
}

// store the old ready function for use later
oldready = ready;

// make a new ready function
ready = function()
{
	// firstly, call the old ready function
	oldready();
	
	// focus on the input box
	$("#input").focus();
	
	// do an initial refresh of the data (all messages, so unread=false)
	// the callback function is the add_intervals function, so the intervals
	// are not added until the first refresh finishes - IMPORTANT
	refreshData(false, add_intervals);
	
	// add the dialogs and events (as defined above)
	add_dialogs();
	add_events();
}
