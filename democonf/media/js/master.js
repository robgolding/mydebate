// 
// Author: Rob Golding
// Project: myDebate
// Group: gp09-sdb
// 

function jquery_alert(title, content, callback)
{
	/* Output a nice alert using jQuery dialogs */
	
	// change the HTML to display the error/alert
	$("#alert").html("<p><span class='ui-icon ui-icon-circle-check' style='float:left; margin:0 7px 50px 0;'></span>"+content+"</p>");
	
	// set the alert title
	$("#alert").dialog('option', 'title', title);
	
	// if there is no callback, then we set the close button to be a useless function
	if (typeof callback != 'undefined')
		$("#alert").dialog('option', 'buttons', {"OK": function() { callback(); $("#alert").dialog('close'); } });
	
	// display the dialog
	$("#alert").dialog('open');
}

ready = function()
{
	/* The default ready function (called when the page loads) */
	
	// setup the alert dialog (for the function above)
	$("#alert").dialog({
		bgiframe: true,
		autoOpen: false,
		closeOnEscape: true,
		draggable: false,
		modal: true,
		resizable: false,
		buttons: {
			"OK": function() { $("#alert").dialog('close'); }
		}
	});
}
