from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, View

from .utils import reset_password
from harvest.models import Property
from member.models import Person, Organization, AuthUser
from member.forms import (
    PersonCreateForm,
    PersonUpdateForm,
    OnboardingPersonUpdateForm,
    OrganizationCreateForm,
    OrganizationForm,
    PasswordChangeForm,
)
from sitebase.models import Email, EmailType


class PersonCreateView(
    PermissionRequiredMixin,
    SuccessMessageMixin[PersonCreateForm],
    CreateView[Person, PersonCreateForm],
):
    permission_required = 'member.add_person'
    model = Person
    form_class = PersonCreateForm
    template_name = 'app/forms/model_form.html'
    success_message = _("New Person registered successfully!")

    def get_context_data(self, **kwargs):
        try:  # registering new owner based on pending property
            p = Property.objects.get(id=self.request.GET['pid'])
            initial = {
                'roles': ['owner'],
                'first_name': p.pending_contact_first_name,
                'family_name': p.pending_contact_family_name,
                'email': p.pending_contact_email,
                'phone': p.pending_contact_phone,
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
                'pending_property_id': p.id,
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
            return reverse_lazy('community-list')

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class PersonUpdateView(
    PermissionRequiredMixin,
    SuccessMessageMixin[PersonUpdateForm],
    UpdateView[Person, PersonUpdateForm],
):
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

    def get_form_kwargs(self, *args, **kwargs):
        """Pass request.user to form"""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['request_user'] = self.request.user
        return kwargs


class OnboardingPersonUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin[OnboardingPersonUpdateForm],
    UpdateView[Person, OnboardingPersonUpdateForm],
):
    model = Person
    form_class = OnboardingPersonUpdateForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Successfully onboarded!")

    def has_permission(self):
        # Only allow onboarding member to update own person
        return self.get_object().pk == self.request.user.person.pk

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Onboarding Person Update")
        context['cancel_url'] = reverse_lazy('home')
        return context

    def get_success_url(self):
        return reverse_lazy('home')


class OrganizationCreateView(
    PermissionRequiredMixin,
    SuccessMessageMixin[OrganizationCreateForm],
    CreateView[Organization, OrganizationCreateForm],
):
    permission_required = 'member.add_organization'
    model = Organization
    form_class = OrganizationCreateForm
    template_name = 'app/forms/organization_create_form.html'
    success_message = _("New Organization registered successfully!")
    success_url = reverse_lazy('organization-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Organization Registration")
        context['cancel_url'] = reverse_lazy('organization-list')
        return context


class OrganizationUpdateView(
    PermissionRequiredMixin,
    SuccessMessageMixin[OrganizationForm],
    UpdateView[Organization, OrganizationForm],
):
    permission_required = 'member.change_organization'
    model = Organization
    form_class = OrganizationForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Organization updated successfully!")
    success_url = reverse_lazy('organization-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Organization Update")
        context['cancel_url'] = reverse_lazy('organization-list')
        return context


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'registration/change_password.html'
    form_class = PasswordChangeForm

    def get_success_url(self):
        messages.success(self.request, _("Password successfully changed!"))
        return reverse('home')


class PasswordResetView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin[PasswordResetForm],
    View,
):
    """View for sending reset password email, with redirect on success."""

    permission_required = 'member.change_authuser'

    def dispatch(self, request, *args, **kwargs):
        user = AuthUser.objects.get(id=self.kwargs['pk'])

        if user.password == '':
            messages.error(
                request,
                _(
                    "Cannot reset password for {email}: User does not have a password set."
                ).format(email=user.email),
            )
            return redirect('community-list')

        m = Email.objects.create(
            recipient=user.person,
            type=EmailType.PASSWORD_RESET,
        )

        if m.send(data={'password': reset_password(user)}) == 1:
            messages.success(
                request,
                _("Password reset email successfully sent to {email}").format(
                    email=user.email
                ),
            )
        else:
            user.password = ''
            user.has_temporary_password = False
            user.save()
            messages.error(
                request,
                _("Failed to send password reset email to {email}").format(
                    email=user.email
                ),
            )

        return redirect('community-list')
