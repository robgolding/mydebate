join_threshold_overrides = {5: 2, 10: 3, 15: 5, 20: 7, 30: 10, 45: 15, 60: 20, 90: 30, 120: 40}

function calculate_join_threshold(period_length)
{
	o = join_threshold_overrides[period_length];
	
	if (o)
	{
		return o;
	}
	else
	{
		return Math.round(period_length*0.35);
	}
}

function place_slider(val)
{
	$("#join-threshold-slider").slider('option', 'value', val);
}

function set_slider_max(val)
{
	$("#join-threshold-slider").slider('option', 'max', val);
}

function reset_slider()
{
	p = $("#id_period_length").val();
	max = p-1;
	set_slider_max(max);
	j = calculate_join_threshold(p);
	place_slider(p-j);
	$("#id_join_threshold").val(j);
}

oldready = ready;

ready = function()
{
	oldready();
	
	slider = $("#join-threshold-slider");
	
	slider.slider({
		range: "max",
		min: 1,
		slide: function(event, ui) {
			$("#id_join_threshold").val($("#id_period_length").val() - ui.value);
		}
	});
	
	reset_slider();
	
	$("#id_join_threshold").addClass("read_only");
	$("#id_join_threshold").attr("readonly", "true");
	$("#join_threshold .label").css("float", "left");
	$("#join_threshold .field").addClass("floating_field");
	
	$("#id_period_length").change(reset_slider);
	
	$("#new-choice").click(function() {
		num_forms = parseInt($("#id_form-TOTAL_FORMS").val());
		$("#id_form-TOTAL_FORMS").val(num_forms+1);
		$("#choices ol").append("\
			<div class='field-wrapper' id='choice'>\
			<li>\
				<div class='field'><input id='id_form-"+num_forms+"-choice' type='text' name='form-"+num_forms+"-choice' maxlength='200' /></div>\
			</li>\
			</div>\
		");
		return false;
	});
	
	
	/*
	$("div.field-wrapper#join_threshold").html("\
		<div style='font-size: 0.9em'>Prevent new members joining when there is less than <input type='text' id='id_join_threshold' name='join_threshold' class='read_only' value='"+join_threshold.val()+"' readonly /> minutes remaining before the next poll.</div> \
	");
	*/
}
