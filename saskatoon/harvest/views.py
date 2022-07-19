from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import ordinal

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404

from django.views.generic import TemplateView, CreateView, UpdateView

from harvest.forms import (PropertyForm, PropertyCreateForm, PublicPropertyForm,
                           EquipmentForm, HarvestForm, RequestForm, RFPManageForm, CommentForm)
from harvest.models import (Equipment, Harvest, HarvestYield, Property,
                            RequestForParticipation, Comment)


class EquipmentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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


class EquipmentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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


class PropertyCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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


class HarvestCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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
            cancel_url = reverse_lazy('harvest-list')

        context = super().get_context_data(**kwargs)
        context['title'] = _("Add a new harvest")
        context['cancel_url'] = cancel_url
        return context

    def get_success_url(self):
        return reverse_lazy('harvest-detail', kwargs={'pk': self.object.pk})


class HarvestUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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
    model = RequestForParticipation
    template_name = 'app/participation_create.html'
    form_class = RequestForm
    success_message = _("Thanks for your interest in participating in this harvest! Your request has been sent and a pick leader will contact you soon.")

    # Overriding to serve harvest info along with the form
    def get(self, request, *args, **kwargs):
        harvest_obj = Harvest.objects.get(id=request.GET['hid'])
        context = {'form': RequestForm(), 'harvest': harvest_obj}
        return render(request, 'app/participation_create.html', context)

    def get_success_url(self):
        request = self.request.GET
        if self.request.user.is_authenticated:
            return reverse_lazy('harvest-detail', kwargs={'pk': request['hid']})
        else:
            return reverse_lazy('calendar')


class RequestForParticipationUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = RequestForParticipation
    form_class = RFPManageForm
    template_name = 'app/participation_manage.html'
    success_message = _("Request updated successfully!")

    # Prefill form based on request for participation (rfp) instance
    def get(self, request, pk, *args, **kwargs):
        rfp = RequestForParticipation.objects.get(id=pk)

        if rfp.is_cancelled == True:
            status = 'cancelled'
        elif rfp.is_accepted == True:
            status = 'accepted'
        elif rfp.is_accepted == False:
            status = 'refused'
        else:
            status = 'pending'

        context = {'form': RFPManageForm(initial={'status': status,
                                'notes_from_pickleader': rfp.notes_from_pickleader}),
                   'rfp': rfp}
        return render(request, 'app/participation_manage.html', context)

    def get_success_url(self):
        request = self.request.GET
        return reverse_lazy('harvest-detail', kwargs={'pk': request['hid']})


class CommentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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
    try:
        _yield = HarvestYield.objects.get(id=id)
        _yield.delete()
        messages.warning(request, "Fruit distribution deleted!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except Exception as e:
        raise


@login_required
def harvest_yield_create(request):
    """ handles new fruit distribution form (app/harvest/create_yield.html)"""
    if request.method == 'POST':
        data = request.POST
        try:
            actor_id = data['actor'] # can be empty
        except KeyError:
            #message.error doesn't show red for some reason..
            messages.warning(request,
                             _("New fruit distribution failed: please select a recipient"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        try:
            harvest_id = data['harvest']
            tree_id = data['tree']
            weight = float(data['weight'])
        except Exception as e:
            raise

        if weight <= 0:
            messages.warning(request,
                             _("New fruit distribution failed: weight must be positive"))
        else:
            _yield = HarvestYield(harvest_id = harvest_id,
                                        recipient_id = actor_id,
                                        tree_id = tree_id,
                                        total_in_lb = weight)
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
    user_is_core_or_pick: bool = request.user.groups.filter(
        name__in=["pickleader", "core"]
    ).exists() # checks if user is in the core or pick leader groups

    if user_is_core_or_pick and harvest.pick_leader is None:
        harvest.pick_leader = request.user
        harvest.status = 'Adopted'
        harvest.save()
        messages.success(request, _("You adopted this harvest!"))
    elif not user_is_core_or_pick:
        messages.warning(request, _("You can't adopt this harvest!"))
    else:
        messages.warning(request, _(
            "This harvest already has a pick leader!"))

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
        messages.success(request, _("You successfully left this harvest!"))
    else:
        messages.warning(request, _("You are not this harvest's pick leader!"))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def harvest_status_change(request, id):
    """
    Changes harvest status
    Used in a dropdown at harvest detail status template
    """
    harvest = get_object_or_404(Harvest, id=id)
    current_user = request.user
    status: str = request.GET['status']

    if harvest.pick_leader == current_user and harvest.status != status:
        harvest.status = status
        harvest.save()
        messages.success(
            request,
            _("You changed the Harvest Status to: '{}'!".format(status))
        )
    elif harvest.status == status:
        messages.warning(request, _(
            "The Harvest Status is already set to '{}'!".format(harvest.status)))
    else:
        messages.warning(request, _("You are not the Harvest's pick leader!"))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
