(function ($) {
 "use strict";
	$(document).ready(function() {
        $('#data-table-basic').DataTable( {
            "order": [[ 0, "desc" ]],
            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]
        } );
        $('table.display').DataTable( {
            "order": [[ 0, "desc" ]],
            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]
        } );
        $('table.datatable-minimal').DataTable({
            "paging": false,
            "order": [[ 0, "desc" ]],
            "info": false,
        });

        $("#data-table-basic_length")
        .detach()
        .prependTo("#DataTables_Table_0_wrapper");
    } );
})(jQuery);