// JavaScript de moi

$(document).ready(function(){
						   
$("div.question").click(function() {
	$(this).next().slideToggle();
 });
						   
$(".selectArrow").click(function() {
	$(".selectOptions").slideToggle();
 });

$(".more").click(function() {
	$(".cache").slideToggle();
	$(".more").hide()
 });

//Slider
$('#diapo').bxSlider({
	wrapper_class: 'slides1_wrap',
	mode: 'fade',
	pause: 6500,
	speed: 1600,
	auto: true
	//pager: true
});

});