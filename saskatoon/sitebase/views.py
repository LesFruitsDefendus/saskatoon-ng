import datetime
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView
from harvest.models import Harvest, Property, RequestForParticipation
from harvest.forms import RequestForm
from django.contrib.auth.decorators import login_required

class Index(TemplateView):
    template_name = 'app/index.html'

#@method_decorator(login_required, name='dispatch')
class Calendar(TemplateView):
    template_name = 'app/calendar/view.html'

    def dispatch(self, request, *args, **kwargs):
        return super(Calendar, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Calendar, self).get_context_data(**kwargs)
        context['view'] = "calendar"
        # context['form_request'] = RequestForm()
        return context
class JsonCalendar(View):

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        harvests = Harvest.objects.filter(end_date__lte=end_date, start_date__gte=start_date)
        events = []
        for harvest in harvests:

            if (harvest.start_date and harvest.end_date and
                    self.request.user.is_staff) or harvest.is_publishable():
                # https://fullcalendar.io/docs/v4/event-object
                event = dict()
                event['url'] = '/participation/create?hid='+str(harvest.id)
                colors = {'Date-scheduled': "#f0ad4e",
                          'Ready': "#337ab7",
                          'Succeeded': "26B99A",
                          'Cancelled': "#D9534F"}
                event['color'] = colors.get(harvest.status, "#ededed")
                event['textColor'] = "#111"

                trees = [t.fruit_name for t in harvest.trees.all()]
                event["title"] = ", ".join(trees)
                if harvest.property.neighborhood.name != "Other":
                    event["title"] += " - "+harvest.property.neighborhood.name

                # http://fullcalendar.io/docs/timezone/timezone/
                event['allday'] = "false"
                if harvest.start_date:
                    event["start"] = harvest.get_local_start()
                if harvest.end_date:
                    event["end"] = harvest.get_local_end()

                # additional info passed to 'extendedProps'
                requests_count = RequestForParticipation.objects.filter(harvest=harvest).count()
                print("requests_count", requests_count)

                event['extendedProps'] = {
                    'harvest_id': harvest.id,
                    'description': harvest.about,
                    'status': harvest.status,
                    'nb_required_pickers': harvest.nb_required_pickers,
                    'nb_requests': requests_count,
                    'trees': trees,
                    'total_harvested': harvest.get_total_distribution()
               }

                events.append(event)
                del event

        return JsonResponse(events, safe=False)
