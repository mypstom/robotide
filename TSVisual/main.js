
$(document).ready(function($) {
	$('.ts-logo').hover(function(){
		$(this).trigger('startRumble');
		}, function(){
		$(this).trigger('stopRumble');
	});
	$('.ts-logo').jrumble({
		x: 3,
		y: 3,
		rotation: 1
	});	
});