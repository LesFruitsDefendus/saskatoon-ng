$(document).ready(function () {
    if($(window).width() > 768){
        $('.collapse').collapse('show');
    }

    const filterPanel = document.getElementById('filter-panel');
    
    if (filterPanel) {
        const observer = new ResizeObserver(entries => {
            for (let entry of entries) {
                const width = entry.contentRect.width;
                const paddingRight = 24; // px
                
                $('.select2-selection, .select2-container').each(function() {
                    $(this).width(width - paddingRight);
                });
            }
        });
        
        observer.observe(filterPanel);
    }
});
