# coding: utf-8
from ckeditor.widgets import CKEditorWidget
from dal import autocomplete
from datetime import datetime as dt
from django import forms
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from harvest.models import (RequestForParticipation, Harvest, HarvestYield, Comment,
                            Equipment, PropertyImage, HarvestImage, TreeType, Property)
from member.forms import validate_email
from member.models import AuthUser, Person, Organization
from postalcodes_ca import parse_postal_code

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
        if AuthUser.objects.filter(email=email).exists():
            auth_user = AuthUser.objects.get(email=email) #email field is unique

            # check if email already requested for the same harvest
            if RequestForParticipation.objects.filter(picker=auth_user.person,
                    harvest_id=self.cleaned_data['harvest_id']).exists():
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
        instance.harvest = harvest_obj

        if auth_user_count > 0:  # user is already in the database
            auth_user = AuthUser.objects.get(email=email)
            instance.picker = auth_user.person
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

            group, __ = Group.objects.get_or_create(name='volunteer')
            auth_user.groups.add(group)

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
            'pending',
            _("Pending")
        ),
        (
            'accepted',
            _('Accept this request')
        ),
        (
            'refused',
            _("Refuse this request")
        ),
        (
            'cancelled',
            _("Canceled by picker")
        )
    ]

    status = forms.ChoiceField(
        label=_('Participation request status'),
        choices=STATUS_CHOICES,
        widget=forms.RadioSelect(),
        required=True
    )

    class Meta:
        model = RequestForParticipation
        fields = ['status', 'notes_from_pickleader']

    def save(self):
        instance = super(RFPManageForm, self).save(commit=False)
        status = self.cleaned_data['status']
        instance.is_cancelled = (status == 'cancelled')
        instance.acceptation_date = dt.now() if status == 'accepted' else None
        instance.is_accepted = {'accepted': True, 'refused': False}.get(status, None)
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

        image = forms.ImageField(
            label='Image',
            widget=forms.ClearableFileInput(attrs={'multiple': True})
        )


class HarvestImageForm(forms.ModelForm):
    class Meta:
        model = HarvestImage
        fields = [
            'image'
        ]


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ['longitude', 'latitude', 'geom', 'changed_by',
                   'pending_contact_first_name', 'pending_contact_family_name',
                   'pending_contact_phone', 'pending_contact_email',
                   'pending_recurring', 'pending_newsletter']

        widgets = {
            'owner': autocomplete.ModelSelect2('owner-autocomplete'),
            'trees': autocomplete.ModelSelect2Multiple('tree-autocomplete'),
            'additional_info': forms.Textarea(),
            'avg_nb_required_pickers': forms.NumberInput()
        }


    field_order = ['pending', 'is_active', 'authorized', 'owner']

    approximative_maturity_date = forms.DateField(
        input_formats=('%Y-%m-%d',),
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
        )
    )




class PropertyCreateForm(PropertyForm):

    create_new_owner = forms.BooleanField(
        label=_("Register new owner"),
        required=False

    )
    owner_first_name = forms.CharField(
        label=_("First Name"),
        help_text=_("This field is required"),
        required=False
    )

    owner_last_name = forms.CharField(
        label=_("Last Name"),
        required=False
    )

    owner_phone = forms.CharField(
        label=_("Phone"),
        required=False
    )

    owner_email = forms.EmailField(
        label=_("Email"),
        help_text=_("This field is required"),
        required=False
    )


    def clean(self):
        data = super().clean()
        if not data['owner']:
            if data['owner_email'] and data['owner_first_name']:
                validate_email(data['owner_email'])
            else:
                raise forms.ValidationError(
                    _("ERROR: You must either select an Owner \
                    or create a new one and provide their personal information"))
        return data


    def save(self):
        # # create Property instance
        instance = super(PropertyCreateForm, self).save()

        # # create Owner Person/AuthUser
        person = Person.objects.create(
            first_name=self.cleaned_data['owner_first_name'],
            family_name=self.cleaned_data['owner_last_name'],
            phone=self.cleaned_data['owner_phone'])
        person.save()

        auth_user = AuthUser.objects.create(
            email=self.cleaned_data['owner_email'],
            person=person)
        auth_user.set_roles(['owner'])

        # # associate Owner to Property
        instance.owner = person
        instance.save()

        return instance


class PublicPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = (
            'pending_contact_first_name',
            'pending_contact_family_name',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avg_nb_required_pickers'].widget.attrs['min'] = 1
        self.fields['number_of_trees'].widget.attrs['min'] = 1
        self.fields['fruits_height'].widget.attrs['min'] = 1
        self.fields['street_number'].widget.attrs['min'] = 0.0
        self.fields['complement'].widget.attrs['min'] = 0.0

    def clean(self):
        cleaned_data = super(PublicPropertyForm, self).clean()
        postal_code = cleaned_data['postal_code'].replace(" ", "")

        try:
            postal_code = parse_postal_code(postal_code)
        except ValueError as invalid_postal_code:
            raise forms.ValidationError(str(invalid_postal_code))

        cleaned_data['postal_code'] = postal_code
        return cleaned_data


class HarvestForm(forms.ModelForm):

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
            'publication_date',
            'nb_required_pickers',
            'about',
        )
        widgets = {
            'trees': autocomplete.ModelSelect2Multiple(
                'tree-autocomplete'
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

    about = forms.CharField(
        widget=CKEditorWidget(),
        label=_("Public announcement"),
        required=True
    )

    start_date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M', '%d/%m/%Y %H:%M:%S'],
        required=True
    )
    end_date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M', '%d/%m/%Y %H:%M:%S'],
        required=True
    )

    publication_date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M', '%d/%m/%Y %H:%M:%S'],
        label=_("Publication date (OPTIONAL)"),
        help_text=_("Leave this field empty to publish harvest as soon as possible"),
        required=False
    )

    def clean_pick_leader(self):
        """check if pick-leader was selected"""
        pickleader = self.cleaned_data['pick_leader']
        status = self.cleaned_data['status']
        if not pickleader and status not in ["To-be-confirmed", "Orphan"]:
            raise forms.ValidationError(
                _("You must choose a pick leader or change harvest status")
            )
        return pickleader


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
