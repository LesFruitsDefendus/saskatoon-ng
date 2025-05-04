from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import ordinal
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone as tz
from django.views.generic import CreateView, UpdateView
from logging import getLogger

from harvest.forms import (
    CommentForm,
    EquipmentForm,
    HarvestForm,
    PropertyCreateForm,
    PropertyForm,
    PublicPropertyForm,
    RFPForm,
    RFPManageForm,
)
from harvest.models import (
    Comment,
    Equipment,
    Harvest,
    HarvestYield,
    Property,
    RequestForParticipation as RFP,
)
from member.models import Organization
from member.permissions import is_core_or_admin, is_pickleader_or_core_or_admin
from sitebase.models import EmailType
from sitebase.utils import to_datetime

logger = getLogger('saskatoon')


class EquipmentCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'harvest.add_equipment'
    model = Equipment
    form_class = EquipmentForm
    template_name = 'app/forms/model_form.html'
    success_url = reverse_lazy('equipment-list')
    success_message = _("Equipment created successfully!")

    def get_organization(self):
        """If creating new harvest from Organization page"""
        try:
            aid = self.request.GET['aid']
            return Organization.objects.get(actor_id=aid)
        except (KeyError, Organization.DoesNotExist):
            return None

    def get_initial(self):
        initial = {}
        _organization = self.get_organization()
        if _organization:
            initial['owner'] = _organization
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Add new equipment")
        context['cancel_url'] = reverse_lazy('equipment-list')
        return context


class EquipmentUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'harvest.change_equipment'
    model = Equipment
    form_class = EquipmentForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Equipment updated successfully!")
    success_url = reverse_lazy('equipment-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Edit equipment")
        context['cancel_url'] = reverse_lazy('equipment-list')
        return context


class PropertyCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'harvest.add_property'
    model = Property
    form_class = PropertyCreateForm
    template_name = 'app/forms/property_create_form.html'
    success_url = reverse_lazy('property-list')
    success_message = _("Property created successfully!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Add a new property")
        context['cancel_url'] = reverse_lazy('property-list')
        return context


class PropertyCreatePublicView(SuccessMessageMixin, CreateView):
    """Public View"""

    model = Property
    form_class = PublicPropertyForm
    template_name = 'app/forms/property_create_public.html'
    success_url = reverse_lazy('property-thanks')
    success_message = _(
        "Thank you for registering your property! \
        A community member will be contacting you as soon as possible"
    )


class PropertyUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'harvest.change_property'
    model = Property
    form_class = PropertyForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Property updated successfully!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Edit property")
        context['cancel_url'] = reverse_lazy(
            'property-detail',
            kwargs={'pk': self.object.pk}
        )
        return context

    def get_success_url(self):
        return reverse_lazy('property-detail', kwargs={'pk': self.object.pk})


class HarvestCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'harvest.add_harvest'
    model = Harvest
    form_class = HarvestForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Harvest created successfully!")

    def get_property(self):
        """If creating new harvest from Property page"""
        try:
            pid = self.request.GET['pid']
            return Property.objects.get(id=pid)
        except (KeyError, Property.DoesNotExist):
            return None

    def get_initial(self):
        initial = {}
        _property = self.get_property()
        if _property:
            initial['property'] = _property
            initial['trees'] = _property.trees.all()

        if 'Pick Leader' in self.request.user.roles:
            initial['pick_leader'] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        _property = self.get_property()
        if _property:
            cancel_url = reverse_lazy(
                'property-detail',
                kwargs={'pk': _property.id}
            )
        else:
            cancel_url = reverse_lazy('harvest-list')

        context = super().get_context_data(**kwargs)
        context['title'] = _("Add a new harvest")
        context['cancel_url'] = cancel_url
        return context

    def get_success_url(self):
        return reverse_lazy('harvest-detail', kwargs={'pk': self.object.pk})


class HarvestUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'harvest.change_harvest'
    model = Harvest
    form_class = HarvestForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Harvest updated successfully!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Edit harvest")
        context['cancel_url'] = reverse_lazy(
            'harvest-detail',
            kwargs={'pk': self.object.pk}
        )
        return context

    def get_success_message(self, cleaned_data) -> str:
        if self.object.status is Harvest.Status.SUCCEEDED:
            pick_leader = self.object.pick_leader
            harvests_as_pickleader = pick_leader.person.harvests_as_pickleader
            harvests_this_year = harvests_as_pickleader.filter(
                start_date__year=tz.now().date().year
            )
            harvest_number: int = harvests_this_year.count()
            success_message_harvest_successful: str = _(
                "You’ve just led your {} fruit harvest! \
                Thank you for supporting your community!"
            ).format(ordinal(harvest_number))
            return success_message_harvest_successful % cleaned_data
        return self.success_message

    def get_success_url(self):
        return reverse_lazy('harvest-detail', kwargs={'pk': self.object.pk})


class RequestForParticipationCreateView(SuccessMessageMixin, CreateView):
    """Public RFP View"""

    model = RFP
    template_name = 'app/forms/participation_create_form.html'
    form_class = RFPForm
    success_message = _("Thanks for your interest in participating in this harvest! \
    Your request has been sent and a pick leader will contact you soon.")

    def get_form_kwargs(self, *args, **kwargs):
        try:
            self.harvest = Harvest.objects.get(id=self.kwargs.get('hid'))
        except Harvest.DoesNotExist as e:
            self.harvest = None
            logger.error(e)

        return super().get_form_kwargs(*args, **kwargs) | {'harvest': self.harvest}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.harvest is None:
            return context | {'error': _("Something went wrong")}

        if (
                (
                    self.request.user.is_authenticated and
                    self.harvest.is_open_to_requests(False)
                ) or
                self.harvest.is_open_to_requests(True)
        ):
            return context | {
                'title': _("Request to join this harvest"),
                'harvest': self.harvest,
            }

        return context | {'error': _(
            "Sorry, this harvest is not open for requests. \
            You can check the calendar for other harvests.")}

    def get_success_url(self):
        if self.request.user.is_authenticated and self.harvest is not None:
            return reverse_lazy(
                'harvest-detail',
                kwargs={'pk': self.harvest.id}
            )
        return reverse_lazy('calendar')


class RequestForParticipationUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'harvest.change_requestforparticipation'
    model = RFP
    form_class = RFPManageForm
    template_name = 'app/forms/participation_manage_form.html'
    success_message = _("Request updated successfully!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Request For Participation")
        context['cancel_url'] = self.get_success_url()
        context['rfp'] = self.object

        action = self.kwargs.get('action')
        if action is not None:
            for a in RFP.Action.choices:
                if action == a[0]:
                    context['save'] = a[1].upper()

        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['status'], kwargs['emailType'] = {
                RFP.Action.ACCEPT: (RFP.Status.ACCEPTED, EmailType.SELECTED_PICKER),
                RFP.Action.DECLINE: (RFP.Status.DECLINED, EmailType.REJECTED_PICKER),
        }.get(self.kwargs.get('action'), (None, None))
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'harvest-detail',
            kwargs={'pk': self.object.harvest.id}
        )


class CommentCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'harvest.add_comment'
    model = Comment
    form_class = CommentForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Comment added!")

    def get_form_kwargs(self, *args, **kwargs):
        """Retrieve harvest object and comment author"""

        self.author = self.request.user
        try:
            self.harvest = Harvest.objects.get(id=self.kwargs.get('hid'))
        except Harvest.DoesNotExist:
            raise Exception('Invalid Harvest ID provided')

        return super().get_form_kwargs(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Add new comment")
        context['cancel_url'] = self.get_success_url()
        return context

    def form_valid(self, form):
        form.instance.author = self.author
        form.instance.harvest = self.harvest
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'harvest-detail',
            kwargs={'pk': self.harvest.id}
        )


@login_required
def harvest_yield_delete(request, id):
    """ deletes a fruit distribution entry (app/harvest/delete_yield.html)"""

    if not is_pickleader_or_core_or_admin(request.user):
        messages.error(
            request,
            _("You must be a pickleader to delete a fruit distribution entry!")
        )
    else:
        _yield = HarvestYield.objects.get(id=id)
        _yield.delete()
        messages.warning(request, "Fruit distribution deleted!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def harvest_yield_create(request):
    """ handles new fruit distribution form (app/harvest/create_yield.html)"""

    if not is_pickleader_or_core_or_admin(request.user):
        messages.error(
            request,
            _("You must be a pickleader to add a fruit distribution entry!")
        )
    elif request.method == 'POST':
        data = request.POST
        try:
            actor_id = data['actor']  # can be empty
        except KeyError:
            messages.error(request,
                           _("New fruit distribution failed: please select a recipient"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        harvest_id = data['harvest']
        tree_id = data['tree']
        weight = float(data['weight'])

        if weight <= 0:
            messages.warning(request,
                             _("New fruit distribution failed: weight must be positive"))
        else:
            _yield = HarvestYield(
                harvest_id=harvest_id,
                recipient_id=actor_id,
                tree_id=tree_id,
                total_in_lb=weight
            )
            _yield.save()
            messages.info(request, _("New Fruit Recipient successfully added!"))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def harvest_adopt(request, id):
    """
    Adds harvest pickleader and changes status to Adopted
    Used in a button at harvest-detail/status template
    """
    harvest = get_object_or_404(Harvest, id=id)

    if not is_pickleader_or_core_or_admin(request.user):
        messages.error(
            request,
            _("You must be a pickleader to adopt this harvest!")
        )
    elif harvest.pick_leader is None:
        harvest.pick_leader = request.user
        harvest.status = Harvest.Status.ADOPTED
        harvest.save()
        messages.info(request, _("You successfully adopted this harvest!"))
    else:
        messages.error(request, _("This harvest already has a pickleader!"))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def harvest_status_change(request, id):
    """
    Changes harvest status from the harvest detail dropdown menu
    """
    harvest = get_object_or_404(Harvest, id=id)
    request_status: str = request.GET['status']

    if harvest.status == request_status:
        messages.warning(
            request,
            _("Harvest status already set to: {}").format(harvest.get_status_display())
        )
    elif is_core_or_admin(request.user) or request.user == harvest.pick_leader:
        if request_status == Harvest.Status.ORPHAN:
            unresolved_requests = harvest.requests.filter(
                status__in=[RFP.Status.PENDING, RFP.Status.ACCEPTED]
            )
            if unresolved_requests.exists():
                messages.warning(
                    request,
                    _("You can't leave this harvest as there are unresolved requests.")
                )
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            harvest.pick_leader = None
            messages.warning(request, _("This harvest no longer have any pick leader"))
        else:
            messages.success(
                request,
                _("Harvest status successfully set to: {}").format(harvest.get_status_display())
            )

        harvest.status = request_status
        harvest.save()
        messages.info(
            request,
            _("Harvest status successfully set to: {}").format(harvest.get_status_display())
        )
    else:
        messages.warning(request, _("You are not authorized to update this harvest status."))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def property_create_orphans(request, id):
    """Create Orphan harvest(s) for a given property."""

    property = get_object_or_404(Property, id=id)

    if not is_core_or_admin(request.user):
        messages.error(
            request,
            _("You must be a core member to create a orphan harvest.")
        )

    if property.pending:
        messages.error(
            request,
            _("Property is has not yet been validated!")
        )

    if not property.authorized:
        messages.error(
            request,
            _("Property is not authorized for this season!")
        )

    harvests = property.harvests.filter(start_date__year=tz.now().date().year)

    num_created = 0
    for t in property.trees.all():
        if not harvests.filter(trees__in=[t]).exists():
            h = Harvest.objects.create(
                status=Harvest.Status.ORPHAN,
                property=property,
                start_date=to_datetime(t.maturity_start),
                end_date=to_datetime(t.maturity_end),
            )
            h.trees.add(t)
            num_created += 1

    if num_created > 0:
        messages.success(
            request,
            _("Successfully created %i orphan harvests").format(num_created)
        )
    else:
        messages.warning(
            request,
            _("Property already has registered harvests for this season")
        )

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
