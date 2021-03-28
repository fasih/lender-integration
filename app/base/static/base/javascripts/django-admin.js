(function($){

	$(document).ready(function(){

		$("a.stopPropagation").click(function(event){
		  event.stopPropagation();
		});

		$('.copyClipboard').click(function(event){
			let data = $(this).data('copy');
			let dummy = $('<input>').val(data).appendTo('body').select();
			document.execCommand('copy');
			event.stopPropagation();
			return false;
		});
	});

})($);

