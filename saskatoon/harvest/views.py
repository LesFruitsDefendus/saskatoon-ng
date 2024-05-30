from django.http.response import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import ordinal

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView

from harvest.forms import (PropertyForm, PropertyCreateForm, PublicPropertyForm,
                           EquipmentForm, HarvestForm, RequestForm, RFPManageForm, CommentForm)
from harvest.models import (Equipment, Harvest, HarvestYield, Property,
                            RequestForParticipation, Comment)
from member.permissions import is_pickleader_or_core


class EquipmentCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'harvest.add_equipment'
    model = Equipment
    form_class = EquipmentForm
    template_name = 'app/forms/model_form.html'
    success_url = reverse_lazy('equipment-list')
    success_message = _("Equipment created successfully!")

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

    # def get_success_url(self):
    #     return reverse_lazy('equipment-detail', kwargs={'pk': self.object.pk})


class PropertyCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'harvest.add_property'
    model = Property
    form_class = PropertyCreateForm
    template_name = 'app/forms/property_create_form.html'
    # TODO: redirect to property list once pagination is implemented
    # success_url = reverse_lazy('property-list')
    success_url = reverse_lazy('home')
    success_message = _("Property created successfully!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Add a new property")
        # TODO: redirect to property list once pagination is implemented
        # context['cancel_url'] = reverse_lazy('property-list')
        context['cancel_url'] = reverse_lazy('home')
        return context


class PropertyCreatePublicView(SuccessMessageMixin, CreateView):
    """Public View"""

    model = Property
    form_class = PublicPropertyForm
    template_name = 'app/forms/property_create_public.html'
    success_url = reverse_lazy('property-thanks')
    success_message = _("Thanks for adding your property! In case you authorized a harvest for this season, please read the <a href='https://core.lesfruitsdefendus.org/s/bnKoECqGHAbXQqm'>Tree Owner Welcome Notice</a>.")


class PropertyUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'harvest.change_property'
    model = Property
    form_class = PropertyForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Property updated successfully!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Edit property")
        context['cancel_url'] = reverse_lazy('property-detail', kwargs={'pk': self.object.pk})
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
            cancel_url = reverse_lazy('property-detail',
                                      kwargs={'pk': _property.id})
        else:
            # TODO: redirect to harvest list once pagination is implemented
            # cancel_url = reverse_lazy('harvest-list')
            cancel_url = reverse_lazy('home')

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
        context['cancel_url'] = reverse_lazy('harvest-detail', kwargs={'pk': self.object.pk})
        return context

    def get_success_message(self, cleaned_data) -> str:
        if self.object.status == "Succeeded":
            pick_leader = self.object.pick_leader  # must exist (see clean_pick_leader)
            harvests_as_pickleader = pick_leader.person.harvests_as_pickleader
            harvests_this_year = harvests_as_pickleader.filter(
                start_date__year=timezone.now().date().year
            )
            harvest_number: int = harvests_this_year.count()
            success_message_harvest_successful: str = _(
                "You’ve just led your {} fruit harvest! Thank you for supporting your community!"
            ).format(ordinal(harvest_number))
            return success_message_harvest_successful % cleaned_data
        return self.success_message

    def get_success_url(self):
        return reverse_lazy('harvest-detail', kwargs={'pk': self.object.pk})


class RequestForParticipationCreateView(SuccessMessageMixin, CreateView):
    """Public RFP View"""

    model = RequestForParticipation
    template_name = 'app/forms/participation_create_form.html'
    form_class = RequestForm
    success_message = _("Thanks for your interest in participating in this harvest! Your request has been sent and a pick leader will contact you soon.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            harvest = Harvest.objects.get(id=self.request.GET['hid'])
            if self.request.user.is_authenticated or harvest.is_open_to_requests():
                context['title'] = _("Request to join this harvest")
                context['harvest'] = harvest
                context['form'] = RequestForm(initial={'harvest_id': harvest.id})
            else:
                context['error'] = _("Sorry, this harvest is not open for requests. You can check the calendar for other harvests.")
        except KeyError:
            context['error'] = _("Something went wrong")
        return context

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return reverse_lazy('harvest-detail', kwargs={'pk': self.request.GET['hid']})
        else:
            return reverse_lazy('calendar')


class RequestForParticipationUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'harvest.change_request_for_participation'
    model = RequestForParticipation
    form_class = RFPManageForm
    template_name = 'app/forms/participation_manage_form.html'
    success_message = _("Request updated successfully!")

    def get_context_data(self, **kwargs):
        rfp = self.object
        if rfp.is_cancelled == True:
            status = 'cancelled'
        elif rfp.is_accepted == True:
            status = 'accepted'
        elif rfp.is_accepted == False:
            status = 'refused'
        else:
            status = 'pending'

        context = super().get_context_data(**kwargs)
        context['form'] = RFPManageForm(initial={'status': status, 'notes_from_pickleader': rfp.notes_from_pickleader})
        return context

    def get_success_url(self):
        request = self.request.GET
        return reverse_lazy('harvest-detail', kwargs={'pk': request['hid']})


class CommentCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'harvest.change_comment'
    model = Comment
    form_class = CommentForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Comment added!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        harvest_id = self.request.GET['h']
        context['title'] = _("Add new comment")
        context['cancel_url'] = reverse_lazy('harvest-detail', kwargs={'pk': harvest_id})
        return context

    def form_valid(self, form):
        request = self.request.GET
        form.instance.author = self.request.user
        form.instance.harvest = Harvest.objects.get(id=request['h'])
        return super(CommentCreateView, self).form_valid(form)

    def get_success_url(self):
        request = self.request.GET
        return reverse_lazy('harvest-detail', kwargs={'pk': request['h']})


@login_required
def harvest_yield_delete(request, id):
    """ deletes a fruit distribution entry (app/harvest/delete_yield.html)"""

    if not is_pickleader_or_core(request.user):
        messages.error(
            request,
            _("You must be a pickleader to register delete a fruit distribution entry!")
        )
    else:
        _yield = HarvestYield.objects.get(id=id)
        _yield.delete()
        messages.warning(request, "Fruit distribution deleted!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def harvest_yield_create(request):
    """ handles new fruit distribution form (app/harvest/create_yield.html)"""

    if not is_pickleader_or_core(request.user):
        messages.error(
            request,
            _("You must be a pickleader to register add a fruit distribution entry!")
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
            messages.success(request, _("New Fruit Recipient successfully added!"))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def harvest_adopt(request, id):
    """
    Adds harvest pickleader and changes status to Adopted
    Used in a button at harvest-detail/status template
    """
    harvest = get_object_or_404(Harvest, id=id)

    if not is_pickleader_or_core(request.user):
        messages.error(
            request,
            _("You must be a pickleader to adopt this harvest!")
        )
    elif harvest.pick_leader is None:
        harvest.pick_leader = request.user
        harvest.status = 'Adopted'
        harvest.save()
        messages.success(request, _("You successfully adopted this harvest!"))
    else:
        messages.error(request, _("This harvest already has a pickleader!"))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def harvest_leave(request, id):
    """
    Removes harvest pickleader and changes status to Orphan
    Used in a button at harvest-detail/status template
    """
    harvest = get_object_or_404(Harvest, id=id)

    if harvest.pick_leader == request.user:
        harvest.pick_leader = None
        harvest.status = 'Orphan'
        harvest.save()
        messages.success(request, _("You successfully dropped this harvest!"))
    else:
        messages.error(request, _("You are not this harvest's pick leader!"))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def harvest_status_change(request, id):
    """
    Changes harvest status
    Used in a dropdown at harvest detail status template
    """
    harvest = get_object_or_404(Harvest, id=id)
    request_status: str = request.GET['status']

    if harvest.status == request_status:
        messages.warning(
            request,
            _("Harvest status already set to: {}".format(harvest.status))
        )
    elif request.user == harvest.pick_leader:
        harvest.status = request_status
        harvest.save()
        messages.success(
            request,
            _("Harvest status successfully set to: {}".format(request_status))
        )
    else:
        messages.warning(request, _("You are not this harvest's pick leader!"))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class MapView(LoginRequiredMixin, TemplateView):
    template_name = 'map/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['properties'] = Property.objects.all()
        return context


# WARNING: for development purposes only, remove before final merge
def testProperty(request):
    import json
    with open("db/property.json", "r") as read_file:
        data = json.load(read_file)
        return JsonResponse(data, safe=False)

