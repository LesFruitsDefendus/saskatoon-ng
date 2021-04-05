# coding: utf-8

from time import timezone

import datetime
from django import forms
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2MultipleWidget
from harvest.models import *
from member.models import *
from django.core.mail import send_mail
from ckeditor.widgets import CKEditorWidget
from django.utils.safestring import mark_safe

# Request for participation
class RequestForm(forms.ModelForm):
    picker_email = forms.EmailField(
        help_text=_("Enter a valid email address, please."),
        label=_("Email")
    )
    picker_first_name = forms.CharField(
        label=_("First name")
    )
    picker_family_name = forms.CharField(
        label=_("Family name")
    )
    picker_phone = forms.CharField(
        label=_("Phone")
    )
    comment = forms.CharField(
        label=_("Comment"),
        required=False,
        widget=forms.widgets.Textarea()
    )
    harvest_id = forms.CharField(
        widget=forms.HiddenInput()
    )
    notes_from_pickleader = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    def clean(self):
        email = self.cleaned_data['picker_email']
        auth_user_count = AuthUser.objects.filter(email=email).count()
        if auth_user_count > 0:
            # check if email is already in the database
            auth_user = AuthUser.objects.get(email=email)

            harvest_obj = Harvest.objects.get(
                id=self.cleaned_data['harvest_id']
            )

            request_same_user_count = RequestForParticipation.objects.\
                filter(
                    picker=auth_user.person,
                    harvest=harvest_obj
                ).count()

            if request_same_user_count > 0:
                # check if email has requested for the same harvest
                raise forms.ValidationError(
                    _("You have already requested to join this pick.")
                )

    def send_email(self, subject, message, mail_to):
        send_mail(
                subject,
                message,
                'info@lesfruitsdefendus.org',
                mail_to,
                fail_silently=False,
            )

    def save(self):
        instance = super(RequestForm, self).save(commit=False)

        harvest_id = self.cleaned_data['harvest_id']
        first_name = self.cleaned_data['picker_first_name']
        family_name = self.cleaned_data['picker_family_name']
        phone = self.cleaned_data['picker_phone']
        email = self.cleaned_data['picker_email']
        comment = self.cleaned_data['comment']
        harvest_obj = Harvest.objects.get(id=harvest_id)

        # check if the email is already registered
        auth_user_count = AuthUser.objects.filter(email=email).count()

        if auth_user_count > 0:  # user is already in the database
            auth_user = AuthUser.objects.get(email=email)
            instance.picker = auth_user.person
            instance.harvest = harvest_obj
        else:
            # user is not in the database, so create a
            # new one and link it to Person obj

            instance.picker = Person.objects.create(
                first_name=first_name,
                family_name=family_name,
                phone=phone
            )
            auth_user = AuthUser.objects.create(
                email=email,
                person=instance.picker
            )

        # Building email content
        pick_leader_email = list()
        pick_leader_email.append(str(harvest_obj.pick_leader.email))
        pick_leader_name = harvest_obj.pick_leader.person.first_name
        publishable_location = harvest_obj.property.publishable_location
        mail_subject = _(u"New request from ") + \
            "%s %s" % (first_name, family_name)
        message = u"Hi %s, " \
                  u"\n\n" \
                  u"There is a new request from %s to participate " \
                  u"in harvest #%s at '%s'.\n\n" \
                  u"Full name: %s %s\n" \
                  u"Email: %s\n" \
                  u"Phone: %s\n" \
                  u"Comment: %s\n\n" \
                  u"Please contact %s directly and then manage " \
                  u"this request through\n" \
                  u"http://saskatoon.lesfruitsdefendus.org/harvest/%s\n\n" \
                  u"Yours,\n" \
                  u"--\n" \
                  u"Saskatoon Harvest System" % \
                  (
                      pick_leader_name,
                      first_name,
                      harvest_id,
                      publishable_location,
                      first_name,
                      family_name,
                      email,
                      phone,
                      comment,
                      first_name,
                      harvest_id
                  )

        # Sending email to pick leader
        # self.send_email(mail_subject, message, pick_leader_email)

        instance.save()

        return instance

    class Meta:
        model = RequestForParticipation
        fields = [
            'number_of_people',
            'picker_first_name',
            'picker_family_name',
            'picker_email',
            'picker_phone',
            'comment',
            'harvest_id',
            'notes_from_pickleader'
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'content',
        ]

        widgets = {
            'content': forms.Textarea(
                attrs={
                    'placeholder': _(u"Your comment here.")
                }
            ),
        }


# To be used by the pick leader to accept/deny/etc and add
# notes on a picker
class RFPManageForm(forms.ModelForm):
    STATUS_CHOICES = [
        (
            'showed_up',
            _('Picker showed up')
        ),
        (
            'didnt_showed_up',
            _("Picker didn't show up")
        ),
        (
            'cancelled',
            _("Picker cancelled in advance")
        )
    ]

    ACCEPT_CHOICES = [
        (
            'yes',
            _('Accept this request')
        ),
        (
            'no',
            _("Refuse this request")
        ),
        (
            'pending',
            _("Pending")
        )
    ]

    accept = forms.ChoiceField(
        label=_('Please accept or refuse this request :'),
        choices=ACCEPT_CHOICES,
        widget=forms.RadioSelect(),
        required=False
    )

    status = forms.ChoiceField(
        label=_('About the picker participation :'),
        choices=STATUS_CHOICES,
        widget=forms.RadioSelect(),
        required=False
    )

    class Meta:
        model = RequestForParticipation
        fields = ['accept', 'status', 'notes_from_pickleader']

    def save(self):
        instance = super(RFPManageForm, self).save(commit=False)
        status = self.cleaned_data['status']
        accept = self.cleaned_data['accept']

        if accept == 'yes':
            instance.acceptation_date = datetime.datetime.now()
            instance.is_accepted = True
        elif accept == 'no':
            instance.acceptation_date = None
            instance.is_accepted = False
        elif accept == 'pending':
            instance.acceptation_date = None
            instance.is_accepted = None

        instance.save()
        return instance


# Used in admin interface
class RFPForm(forms.ModelForm):
    class Meta:
        model = RequestForParticipation
        fields = '__all__'


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = [
            'image'
        ]


class HarvestImageForm(forms.ModelForm):
    class Meta:
        model = HarvestImage
        fields = [
            'image'
        ]

class PropertyForm(forms.ModelForm):
    trees = forms.ModelMultipleChoiceField(queryset=TreeType.objects.all(), widget=Select2MultipleWidget)

    class Meta:
        model = Property
        fields = (
            'owner',
            'is_active',
            'authorized',
            'pending',
            'trees',
            'trees_location',
            'avg_nb_required_pickers',
            'public_access',
            'trees_accessibility',
            'neighbor_access',
            'compost_bin',
            'ladder_available',
            'ladder_available_for_outside_picks',
            'harvest_every_year',
            'number_of_trees',
            'approximative_maturity_date',
            'fruits_height',
            'street_number',
            'street',
            'complement',
            'postal_code',
            'publishable_location',
            'neighborhood',
            'city',
            'state',
            'country',
            # 'longitude',
            # 'latitude',
            # 'geom',
            'additional_info',
        )

        widgets = {
            'owner': autocomplete.ModelSelect2(
               'actor-autocomplete'
            ),
            'trees': autocomplete.ModelSelect2Multiple(
                'tree-autocomplete'
            ),
            'additional_info': forms.Textarea(),
            'avg_nb_required_pickers': forms.NumberInput()
        }

    approximative_maturity_date = forms.DateField(
        input_formats=('%Y-%m-%d',),
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
        )
    )

class PublicPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = (
            'pending_contact_name',
            'pending_contact_phone',
            'pending_contact_email',
            'pending_recurring',
            'authorized',
            'trees',
            'number_of_trees',
            'approximative_maturity_date',
            'trees_location',
            'trees_accessibility',
#            'public_access',
            'neighbor_access',
            'compost_bin',
            'ladder_available',
            'ladder_available_for_outside_picks',
            'harvest_every_year',
            'avg_nb_required_pickers',
            'fruits_height',
            'street_number',
            'street',
            'complement',
            'postal_code',
            'neighborhood',
            'city',
            'state',
            'country',
            'additional_info',
            'pending_newsletter',
        )

        widgets = {
            'trees': autocomplete.ModelSelect2Multiple(
                'tree-autocomplete'
            ),
            'avg_nb_required_pickers': forms.NumberInput(),
        }


    neighbor_access = forms.BooleanField(
        label = _("Volunteers have permission to go on the neighbours' property to access fruits"),
        required=False,
    )

    compost_bin = forms.BooleanField(
        label = _('I have a compost bin where you can leave rotten fruit'),
        required=False,
    )

    ladder_available= forms.BooleanField(
        label = _('I have a ladder that can be used during the harvest'),
        required=False,
    )

    ladder_available_for_outside_picks = forms.BooleanField(
        label = _('I would lend my ladder for another harvest nearby'),
        required=False,
    )

    harvest_every_year = forms.BooleanField(
        label = _('My tree(s)/vine(s) produce fruit every year (if not, please include info about frequency in additional comments at the bottom)'),
        required=False,
    )

    pending_recurring = forms.ChoiceField(
        label=_('Have you provided us any information about your property before?'),
        choices=[(True,_('Yes')),(False,_('No'))],
        widget=forms.RadioSelect,
    )

    authorized = forms.ChoiceField(
        label=_('Do you give us permission to harvest your tree(s) and/or vine(s) this season?'),
        choices=[(True,_('Yes')),(False,_('Not this year, but maybe in future seasons'))],
        widget=forms.RadioSelect(),
        required=True
    )

    approximative_maturity_date = forms.DateField(
        input_formats=('%Y-%m-%d',),
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
        )
    )

    trees_location = forms.CharField(
        label=_('Location of tree(s) or vine(s)'),
        help_text=_('Location on the property (e.g. Front yard, back yard, etc.)'),
        required=False
    )

    trees_accessibility = forms.CharField(
        label=_('Access to tree(s) or vine(s)'),
        help_text=_('Any info on how to access the tree(s) or vine(s) (e.g. locked gate in back, publicly accessible from sidewalk, etc.)'),
        required=False
    )

    avg_nb_required_pickers = forms.DecimalField(
        label=_('Number of pickers'),
        help_text=_('Approximate number of pickers needed for a two-hour harvesting period.'),
        required=False
    )

    fruits_height = forms.DecimalField(
        label=_('Height of lowest fruits (meters)'),
        required=False
    )

    street_number = forms.DecimalField(
        label=_('Address number'),
        required=True
    )

    number_of_trees = forms.DecimalField(
        label=_('Total number of trees/vines on this property'),
        required=True
    )

    street = forms.CharField(
        label=_('Street name'),
        required=True
    )

    complement = forms.DecimalField(
        label=_('Apartment # (if applicable)'),
        required=False
    )

    postal_code = forms.CharField(
        required=True
    )

    pending_newsletter = forms.BooleanField(
        label=_('I would like to receive emails from Les Fruits Defendus such as newsletters and updates'),
        required=False
    )

    additional_info = forms.CharField(
        help_text=_('Any additional information that we should be aware of (e.g. details about how often tree produces fruit, description of fruit if the type is unknown or not in the list, etc.)'),
        widget=forms.widgets.Textarea(),
        required=False
    )

class HarvestForm(forms.ModelForm):
    about = forms.CharField(
        widget=CKEditorWidget(),
        label=mark_safe(_("Public announcement"))
    )

    class Meta:
        model = Harvest
        help_texts = {
            'status': ' ',
            'property': ' ',
            'trees': ' ',
            'pick_leader': ' ',
            'start_date': ' ',
            'end_date': ' ',
            'nb_required_pickers': ' ',
            'about': ' ',
        }
        fields = (
            'status',
            'property',
            'trees',
            'owner_present',
            'owner_help',
            'owner_fruit',
            'pick_leader',
            'start_date',
            'end_date',
            'nb_required_pickers',
            'about',
        )
        widgets = {
            'trees': autocomplete.ModelSelect2Multiple(
                'tree-autocomplete'
            ),
            'pickers': autocomplete.ModelSelect2Multiple(
                'person-autocomplete'
            ),
            'pick_leader': autocomplete.ModelSelect2(
                'pickleader-autocomplete'
            ),
            'equipment_reserved': autocomplete.ModelSelect2Multiple(
                'equipment-autocomplete'
            ),
            'property': autocomplete.ModelSelect2(
                'property-autocomplete'
            ),
            'nb_required_pickers': forms.NumberInput()
        }

    publication_date = forms.DateTimeField(
        widget=forms.HiddenInput(),
        required=False
    )

    start_date = forms.DateTimeField(
        input_formats=('%Y-%m-%d %H:%M',),
        widget=forms.DateInput(
            format='%Y-%m-%d %H:%M',
        )
    )

    end_date = forms.DateTimeField(
        input_formats=('%Y-%m-%d %H:%M',),
        widget=forms.DateInput(
            format='%Y-%m-%d %H:%M',
        )
    )

    def save(self):
        instance = super(HarvestForm, self).save(commit=False)

        status = self.cleaned_data['status']
        publication_date = self.cleaned_data['publication_date']
        trees = self.cleaned_data['trees']

        if status in ["Ready", "Date-scheduled", "Succeeded"]:
            # if publication_date is None:
            instance.publication_date = timezone.now()

        if status in ["To-be-confirmed", "Orphan", "Adopted"]:
            if publication_date is not None:
                instance.publication_date = None

        if not instance.id:
            instance.save()
        instance.trees.set(trees)
        instance.save()

        return instance


class HarvestYieldForm(forms.ModelForm):
    class Meta:
        model = HarvestYield
        fields = ('__all__')
        widgets = {
            'recipient': autocomplete.ModelSelect2(
                'actor-autocomplete'
            ),
            'tree': autocomplete.ModelSelect2(
                'tree-autocomplete'
            ),
        }


class EquipmentForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(EquipmentForm, self).clean()
        bool1 = bool(self.cleaned_data['property'])
        bool2 = bool(self.cleaned_data['owner'])
        if not (bool1 != bool2):
            raise forms.ValidationError(
                _('Fill in one of the two fields: property or owner.')
            )
        return cleaned_data

    class Meta:
        model = Equipment
        widgets = {
            'property': autocomplete.ModelSelect2(
                'property-autocomplete'
            ),
            'owner': autocomplete.ModelSelect2(
                'actor-autocomplete'
            ),
        }
        fields = '__all__'
