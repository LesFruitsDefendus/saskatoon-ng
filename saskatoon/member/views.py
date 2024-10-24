from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, View
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .utils import send_reset_password_email
from .models import Person, Organization, AuthUser
from harvest.models import Property
from .forms import ( PersonCreateForm, PersonUpdateForm, OnboardingPersonUpdateForm,
                     OrganizationCreateForm, OrganizationForm,
                     PasswordChangeForm)


class PersonCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'member.add_person'
    model = Person
    form_class = PersonCreateForm
    template_name = 'app/forms/model_form.html'
    success_message = _("New Person registered successfully!")

    def get_context_data(self, **kwargs):
        try: # registering new owner based on pending property
            p = Property.objects.get(id=self.request.GET['pid'])
            initial = { 'roles': ['owner'],
                        'phone': p.pending_contact_phone,
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
            # TODO: redirect to community list once pagination is implemented
            # cancel_url = reverse_lazy('community-list')
            cancel_url = reverse_lazy('home')

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
            # TODO: redirect to community list once pagination is implemented
            # return reverse_lazy('community-list')
            return reverse_lazy('home')

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class PersonUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'member.change_person'
    model = Person
    form_class = PersonUpdateForm
    template_name = 'app/forms/model_form.html'
    success_message = _("Person updated successfully!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Person Update")
        # TODO: redirect to community list once pagination is implemented
        # context['cancel_url'] = reverse_lazy('community-list')
        context['cancel_url'] = reverse_lazy('home')
        return context

    def get_success_url(self):
        try:
            property_id = self.request.GET['pid']
            return reverse_lazy('property-detail', kwargs={'pk': property_id})
        except KeyError:
            # TODO: redirect to community list once pagination is implemented
            # return reverse_lazy('community-list')
            return reverse_lazy('home')

    def get_form_kwargs(self, *args, **kwargs):
        """Pass request.user to form"""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['request_user'] = self.request.user
        return kwargs


class OnboardingPersonUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'registration/change_password.html'
    form_class = PasswordChangeForm

    def get_success_url(self):
        messages.success(self.request, _("Password successfully changed!"))
        return reverse('home')


class PasswordResetView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, View):
    """View for sending reset password email, with redirect on success."""
    permission_required = 'member.change_authuser'

    def dispatch(self, request, *args, **kwargs):
        target_user = AuthUser.objects.get(id=self.kwargs['pk'])

        if target_user.password == '':
            messages.error(request, _("Cannot reset password for {email}: User does not have a password set.".format(email=target_user.email)))
            return redirect('community-list')

        subject = "Les Fruits Défendus - Password reset"

        message = """Hi {name},

Your password for the Saskatoon harvest management platform has been reset by an administrator from Les Fruits Défendus. \
Please log in using the temporary credentials provided below and follow the steps to update your new password.

Login page: https://saskatoon.lesfruitsdefendus.org/accounts/login/
Email address: {email}
Temporary password: {{password}}

Thanks for supporting your community!

--

Bonjour {name},

Votre mot de passe pour la plateforme de gestion Saskatoon a été réinitialisé par un.e administrateur.ice des Fruits Défendus. \
Merci de vous connecter en utilisant les identifiants fournis plus bas et de suivre les instructions pour remettre à jour votre nouveau mot de passe.

Page de connexion: https://saskatoon.lesfruitsdefendus.org/accounts/login/
Adresse électronique: {email}
Mot de passe temporaire: {{password}}

Merci de soutenir votre communauté!

--

Les Fruits Défendus
""".format(name=target_user.person.first_name, email=target_user.email)

        if send_reset_password_email(target_user, subject, message):
            messages.success(request, _("Password reset email successfully sent to {email}".format(email=target_user.email)))
        else:
            messages.error(request, _("Failed to send password reset email to {email}".format(email=target_user.email)))

        return redirect('community-list')
