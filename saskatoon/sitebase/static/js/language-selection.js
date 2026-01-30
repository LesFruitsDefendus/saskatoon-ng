$(document).ready(function () {
    $('.change_language').click(function(e){
        e.preventDefault();
        $('#language').val($(this).attr('lang_code'));
        $('#change_language_form').submit();
    });
});
