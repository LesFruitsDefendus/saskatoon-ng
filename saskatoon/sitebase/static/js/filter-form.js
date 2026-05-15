$(document).ready(function () {
    if($(window).width() > 768){
        $('.collapse').collapse('show');
    }

    $('#filter-panel').resize(function(){
        const width = $(this).width()
        const paddingRight = 24; // px
        $('.select2-selection').each(function() {
            $(this).width(width-paddingRight);
        });
    });
});
