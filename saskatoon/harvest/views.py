from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render

from django.views.generic import TemplateView, CreateView, UpdateView

from harvest.forms import (EquipmentForm, PropertyForm, PublicPropertyForm,
                           HarvestForm, RequestForm, RFPManageForm, CommentForm)
from .models import Equipment, Harvest, Property, RequestForParticipation, Comment


class EquipmentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'app/forms/model_form.html'
    success_url = reverse_lazy('equipment-list')
    success_message = "Equipment created successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add new equipment"
        context['cancel_url'] = reverse_lazy('equipment-list')
        return context

class EquipmentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'app/forms/model_form.html'
    success_message = "Equipment updated successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit equipment"
        context['cancel_url'] = reverse_lazy('equipment-list')
        return context

    def get_success_url(self):
            return reverse_lazy('equipment-detail', kwargs={'pk': self.object.pk})

class PropertyCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'app/forms/model_form.html'
    success_url = reverse_lazy('property-list')
    success_message = "Property created successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add a new property"
        context['cancel_url'] = reverse_lazy('property-list')
        return context

class PropertyCreatePublicView(SuccessMessageMixin, CreateView):
    model = Property
    form_class = PublicPropertyForm
    template_name = 'app/property_create_public.html'
    success_url = 'thanks'
    success_message = 'Thanks for adding your property! In case you authorized a harvest for this season, please read the <a href="https://core.lesfruitsdefendus.org/s/bnKoECqGHAbXQqm">Tree Owner Welcome Notice</a>.'

class PropertyUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'harvest.change_property'
    model = Property
    form_class = PropertyForm
    template_name = 'app/forms/model_form.html'
    success_message = "Property updated successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit property"
        context['cancel_url'] = reverse_lazy('property-detail', kwargs={'pk': self.object.pk})
        return context

    def get_success_url(self):
            return reverse_lazy('property-detail', kwargs={'pk': self.object.pk})


class HarvestCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Harvest
    form_class = HarvestForm
    template_name = 'app/forms/model_form.html'
    success_message = "Harvest created successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add a new harvest"
        context['cancel_url'] = reverse_lazy('harvest-list')
        return context

    def get_success_url(self):
            return reverse_lazy('harvest-detail', kwargs={'pk': self.object.pk})

class HarvestUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Harvest
    form_class = HarvestForm
    template_name = 'app/forms/model_form.html'
    success_message = "Harvest updated successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit harvest"
        context['cancel_url'] = reverse_lazy('harvest-detail', kwargs={'pk': self.object.pk})
        return context

    def get_success_url(self):
            return reverse_lazy('harvest-detail', kwargs={'pk': self.object.pk})

class RequestForParticipationCreateView(SuccessMessageMixin, CreateView):
    model = RequestForParticipation
    template_name = 'app/participation_create.html'
    form_class = RequestForm
    success_message = "Thanks for your interest in participating in this harvest! Your request has been sent and a pick leader will contact you soon."

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
    success_message = "Request updated successfully!"

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
    success_message = "Comment added!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        harvest_id = self.request.GET['h']
        context['title'] = "Add new comment"
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
        messages.warning(request, "Fruit Distribution Deleted")
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
            messages.warning(request, "New Fruit Distribution Failed: Please select a recipient")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        try:
            harvest_id = data['harvest']
            tree_id = data['tree']
            weight = float(data['weight'])
        except Exception as e:
            raise

        if weight <= 0:
            messages.warning(request, "New Fruit Distribution Failed: Weight must be positive")
        else:
            _yield = HarvestYield(harvest_id = harvest_id,
                                        recipient_id = actor_id,
                                        tree_id = tree_id,
                                        total_in_lb = weight)
            _yield.save()
            messages.success(request, 'New Fruit Recipient successfully added!')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
