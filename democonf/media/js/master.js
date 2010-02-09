function close_message(id) {
	selector = "#site-message-"+id;
	$(selector).hide();
	return false;
}

ready = function()
{
	$("#site-messages-table tr td.message-close a").click(function() {
		$(this).parent().parent().hide();
		return false;
	});
}
