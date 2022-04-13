(function ($) {
 "use strict";
	$(document).ready(function() {
    $('#data-table-basic').DataTable( {
        "order": [[ 0, "desc" ]],
        "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]
    } );
} );
})(jQuery); 