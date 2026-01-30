$(document).ready(function () {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        expandRows: true,
        slotMinTime: '08:00',
        slotMaxTime: '20:00',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        initialView: 'dayGridMonth',
        navLinks: true, // can click day/week names to navigate views
        nowIndicator: true,
        dayMaxEvents: true, // allow "more" link when too many events
        events: '/jsoncal/',
        eventClick: function(info) {
            info.jsEvent.preventDefault(); // don't link to event['url']

            /* filling modal templates*/
            $('.harvest-id').attr('value', info.event.extendedProps.harvest_id);
            $('.harvest-url').attr('href', "/harvest/" + info.event.extendedProps.harvest_id);
            $('.rfp-url').attr('href', info.event.url);
            $('.modal-title').html(info.event.title);
            $('.start-date').html(info.event.extendedProps.start_date);
            $('.start-time').html(info.event.extendedProps.start_time);
            $('.end-date').html(info.event.extendedProps.end_date);
            $('.end-time').html(info.event.extendedProps.end_time);
            $('.description').html(info.event.extendedProps.description);
            $('.nb-required').html(info.event.extendedProps.nb_required_pickers);
            $('.nb-requests').html(info.event.extendedProps.nb_requests);
            $('.total-harvested').html(info.event.extendedProps.total_harvested);

            switch(info.event.extendedProps.status){
                case "scheduled":
                    $('#scheduledModal').modal();
                    break;
                case "ready":
                    $('#readyModal').modal();
                    break;
                case "succeeded":
                    $('#succeededModal').modal();
                    break;
                case "cancelled":
                    $('#cancelledModal').modal();
                    break;
                case "orphan":
                    $('#orphanModal').modal();
                    break;
                case "adopted":
                    $('#adoptedModal').modal();
                    break;
            }
        },
        eventMouseEnter: function(info) {
            var props = info.event.extendedProps;
            var timeRange = ["orphan", "adopted"].includes(props.status) ?
                            (props.start_date + " - " + props.end_date) :
                            (props.start_time + " - " + props.end_time);
            info.el.title = info.event.title + "\n" + timeRange;
        }
    });

    calendar.render();
});
