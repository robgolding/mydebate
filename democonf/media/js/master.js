function close_message(id) {
	selector = "#site-message-"+id;
	$(selector).hide();
	return false;
}

function jquery_alert(title, content) {
	$("#alert").html("<p><span class='ui-icon ui-icon-circle-check' style='float:left; margin:0 7px 50px 0;'></span>"+content+"</p>");
	$("#alert").dialog('option', 'title', title);
	$("#alert").dialog('open');
}

ready = function()
{
	
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
	
	$("#site-messages-table tr td.message-close a").click(function() {
		$(this).parent().parent().hide();
		return false;
	});
}
