import datetime
from django.utils import timezone as tz
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
    template_name = 'app/calendar.html'

    def dispatch(self, request, *args, **kwargs):
        return super(Calendar, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Calendar, self).get_context_data(**kwargs)

        context['view'] = "calendar"
        context['form_request'] = RequestForm()

        return context

class JsonCalendar(View):
    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        harvests = Harvest.objects.filter(end_date__lte=end_date, start_date__gte=start_date)
        events = []
        for harvest in harvests:
            if (harvest.start_date and
                    harvest.end_date and
                    self.request.user.is_staff) \
                    or harvest.is_publishable():
                text_color = "#ffffff"
                if harvest.status == "Date-scheduled":
                    color = "#f0ad4e"
                elif harvest.status == "Ready":
                    color = "#337ab7"
                elif harvest.status == "Succeeded":
                    color = "#26B99A"
                elif harvest.status == "Cancelled":
                    color = "#D9534F"
                else:
                    color = "#ededed"
                    text_color = "#333"
                event = dict()
                event["harvest_id"] = harvest.id
                event["allday"] = "false"
                event["description"] = harvest.about
                event["status"] = harvest.status
                event["nb_required_pickers"] = harvest.nb_required_pickers
                requests_count = RequestForParticipation.objects.filter(harvest=harvest).count()
                event["nb_requests"] = requests_count
                trees_list = []
                for t in harvest.trees.all():
                    trees_list.append(t.fruit_name)
                event["trees"] = trees_list
                event["title"] = ", ".join(trees_list)
                if harvest.property.neighborhood.name != "Other":
                    event["title"] += " @ "+harvest.property.neighborhood.name

                event["total_harvested"] = harvest.get_total_distribution()

                # https://fullcalendar.io/docs/v4/event-object
                # http://fullcalendar.io/docs/timezone/timezone/
                local_tz = tz.get_current_timezone()
                if harvest.start_date:
                    start = local_tz.localize(harvest.start_date.replace(tzinfo=None))
                    event["start"] = start
                if harvest.end_date:
                    end = local_tz.localize(harvest.end_date.replace(tzinfo=None))
                    event["end"] = end

                event["url"] = '/participation/create?hid='+str(harvest.id)
                event["color"] = color
                event["textColor"] = text_color
                events.append(event)
                del event

        return JsonResponse(events, safe=False)
