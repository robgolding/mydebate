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

function display_time(seconds)
{
	minutes = parseInt(seconds/60);
	seconds = seconds%60;
	
	if (minutes=0) { minutes = "00" };
	if (seconds=0) { seconds = "00" };
	
	return minutes+":"+seconds
	
}
