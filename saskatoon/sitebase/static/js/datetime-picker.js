$(document).ready(function () {
    var datetimeFormat = 'Y-m-d H:i';

    $("#id_start_date").datetimepicker({format: datetimeFormat});
    $("#id_end_date").datetimepicker({format: datetimeFormat});
    $("#id_publication_date").datetimepicker({format: datetimeFormat});

    var dateFormat = 'Y-m-d';
    $("#id_approximative_maturity_date").datetimepicker({format: dateFormat});
});
