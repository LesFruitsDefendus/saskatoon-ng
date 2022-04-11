
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from .models import Person, Organization
from harvest.models import Property
from .forms import ( PersonCreateForm, PersonUpdateForm,
                     OrganizationCreateForm, OrganizationForm )

class PersonCreateView(SuccessMessageMixin, CreateView):
    model = Person
    form_class = PersonCreateForm
    template_name = 'app/forms/model_form.html'
    success_message = _("New Person registered successfully!")

    def get_context_data(self, **kwargs):
        try: # registering new owner based on pending property
            p = Property.objects.get(id=self.request.GET['pid'])
            initial = { 'roles': ['owner'],
                        'first_name': p.pending_contact_name,
                        'phone': p.pending_contact_phone.replace(" ", "-"),
                        'email': p.pending_contact_email,
                        'street_number': p.street_number,
                        'street': p.street,
                        'complement': p.complement,
                        'postal_code': p.postal_code,
                        'neighborhood': p.neighborhood,
                        'city': p.city,
                        'state': p.state,
                        'country': p.country,
                        'newsletter_subscription': p.pending_newsletter,
                        'comments': p.additional_info,
                        'pending_property_id': p.id
            }
            cancel_url = '/property/' + str(p.id)
        except KeyError:
            initial = None
            cancel_url = reverse_lazy('community-list')

        context = super().get_context_data(**kwargs)
        context['title'] = _("Person Registration")
        context['form'] = PersonCreateForm(initial=initial)
        context['cancel_url'] = cancel_url
        return context

    def get_success_url(self):
        try:
            property_id = self.request.GET['pid']
            return reverse_lazy('property-detail', kwargs={'pk': property_id})
        except KeyError:
            return reverse_lazy('home')

class PersonUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'member.change_person'
    model = Person
    form_class = PersonUpdateForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Person updated successfully!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Person Update")
        context['cancel_url'] = reverse_lazy('community-list')
        return context

    def get_success_url(self):
        try:
            property_id = self.request.GET['pid']
            return reverse_lazy('property-detail', kwargs={'pk': property_id})
        except KeyError:
            return reverse_lazy('community-list')

class OrganizationCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'member.add_organization'
    model = Organization
    form_class = OrganizationCreateForm
    template_name = 'app/forms/organization_create_form.html'
    success_message = _("New Organization registered successfully!")
    success_url = reverse_lazy('beneficiary-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Organization Registration")
        context['cancel_url'] = reverse_lazy('beneficiary-list')
        return context

class OrganizationUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'member.change_organization'
    model = Organization
    form_class = OrganizationForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Organization updated successfully!")
    success_url = reverse_lazy('beneficiary-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Organization Update")
        context['cancel_url'] = reverse_lazy('beneficiary-list')
        return context
