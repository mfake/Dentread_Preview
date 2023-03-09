$(document).ready(function(){

	$("#get-data-form").submit(function(e){

		var content = tinymce.get("full-featured-non-premium").getContent();

		$("#data-container").html(content);

		return false;

	});

});