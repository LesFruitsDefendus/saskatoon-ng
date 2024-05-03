import os
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView
from harvest.models import Harvest, RequestForParticipation
from member.models import  AuthUser
from saskatoon.settings import EQUIPMENT_POINTS_PDF_PATH, VOLUNTEER_WAIVER_PDF_PATH
from sitebase.models import Content

VOLUNTEER_HOME_CONTENT_NAME = 'volunteer_home'
PICKLEADER_HOME_CONTENT_NAME = 'pickleader_home'
TERMS_CONDITIONS_CONTENT_NAME = 'terms_conditions'
PRIVACY_POLICY_CONTENT_NAME = 'privacy_policy'


class Index(TemplateView):
    template_name = 'app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        content_name = VOLUNTEER_HOME_CONTENT_NAME

        if self.request.user.is_authenticated:
            content_name = PICKLEADER_HOME_CONTENT_NAME

        home, _ = Content.objects.get_or_create(name=content_name)
        context['content'] = home.content(self.request.LANGUAGE_CODE)

        return context

    def dispatch(self, request, *args, **kwargs):
        """Redirect new pickleaders"""

        user = self.request.user

        if user.is_authenticated:
            if not user.password_set:
                return redirect('change_password')

            if user.is_onboarding:
                return redirect('terms_conditions')

        return super().dispatch(request, *args, **kwargs)


class TermsConditionsView(LoginRequiredMixin, TemplateView):
    """
    Show terms and conditions.
    """
    template_name = 'app/terms_conditions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        terms, _ = Content.objects.get_or_create(name=TERMS_CONDITIONS_CONTENT_NAME)
        context['content'] = terms.content(self.request.LANGUAGE_CODE)

        return context

class PrivacyPolicyView(TemplateView):
    template_name = 'app/privacy_policy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        content_name = PRIVACY_POLICY_CONTENT_NAME

        privacy_policy, _ = Content.objects.get_or_create(name=content_name)
        context['content'] = privacy_policy.content(self.request.LANGUAGE_CODE)

        return context


@method_decorator(login_required, name='dispatch')
class RestrictedPDFView(View):
    """Serve PDF file for specific user groups"""

    ALLOWED_GROUPS = ['admin', 'core', 'pickleader']
    PDF_PATH = ""  # absolute path

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=self.ALLOWED_GROUPS).exists():
            try:
                with open(self.PDF_PATH, 'rb') as pdf:
                    return HttpResponse(pdf, content_type='application/pdf')
            except FileNotFoundError:
                return handler404(request, FileNotFoundError)
        else:
            return handler403(request, PermissionDenied)


class EquipmentPointsPDFView(RestrictedPDFView):
    PDF_PATH = EQUIPMENT_POINTS_PDF_PATH


class VolunteerWaiverPDFView(RestrictedPDFView):
    PDF_PATH = VOLUNTEER_WAIVER_PDF_PATH


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
            if ( harvest.start_date and harvest.end_date and
                    (self.request.user.is_staff or harvest.is_publishable()) ):
                # https://fullcalendar.io/docs/event-object
                event = dict()
                event['url'] = '/participation/create?hid='+str(harvest.id)
                colors = ({'Date-scheduled': "#FFE180",
                           'Ready': "#BADDFF",
                           'Succeeded': "#9CF0DB",
                           'Cancelled': "#ED6D62"})
                event['display'] = "block"
                event['backgroundColor'] = colors.get(harvest.status, "#ededed")
                event['borderColor'] = event['backgroundColor']
                event['textColor'] = "#2A3F54"
                event['title'] = harvest.get_public_title()

                # http://fullcalendar.io/docs/timezone/timezone/
                event['allday'] = "false"
                if harvest.start_date:
                    event['start'] = harvest.get_local_start()
                if harvest.end_date:
                    event['end'] = harvest.get_local_end()

                # additional info passed to 'extendedProps'
                requests_count = RequestForParticipation.objects.filter(harvest=harvest).count()

                event['extendedProps'] = {
                    'start_date': event['start'].strftime("%a. %b. %-d, %Y"),
                    #TODO handle scenario when end_date > start_date
                    'start_time': event['start'].strftime("%-I:%M %p"),
                    'end_time': event['end'].strftime("%-I:%M %p"),
                    'harvest_id': harvest.id,
                    'description': harvest.about,
                    'status': harvest.status,
                    'nb_required_pickers': harvest.nb_required_pickers,
                    'nb_requests': requests_count,
                    'trees': harvest.get_fruits(),
                    'total_harvested': harvest.get_total_distribution()
               }

                events.append(event)
                del event

        return JsonResponse(events, safe=False)


def handler400(request, exception):
    return render(request, 'app/errors/400.html')


def handler403(request, exception):
    return render(request, 'app/errors/403.html')


def handler404(request, exception):
    return render(request, 'app/errors/404.html')


def handler500(request):
    return render(request, 'app/errors/500.html')


def handler403_csrf_failue(request, reason=""):
    return render(request, 'app/errors/403_csrf.html')
