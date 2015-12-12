function validate_food_preferences(stuff) {
  var val = $('#food-preferences select').val();
  if (val == 'Other') {
    $('#food-other').show();
  } else {
    $('#food-other').hide();
  }
}
function validate_location(stuff) {
	var val = $('#location select').val();
	if (val == 'WMU') {
		$('#help-text').show();
	} else {
		$('#help-text').hide();
	}
}
