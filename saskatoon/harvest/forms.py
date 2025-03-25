from django_quill.forms import QuillFormField
from dal import autocomplete
from datetime import datetime as dt
from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from logging import getLogger
from postalcodes_ca import parse_postal_code

from harvest.models import (
    Comment,
    Equipment,
    Harvest,
    HarvestYield,
    Property,
    RequestForParticipation as RFP,
)
from member.forms import validate_email
from member.models import AuthUser, Person
from sitebase.models import Email, EmailType
from sitebase.serializers import EmailRFPSerializer


logger = getLogger('saskatoon')


class RFPForm(forms.ModelForm):
    """Request For Participation form."""

    class Meta:
        model = RFP
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'number_of_pickers',
            'comment',
        ]

        labels = {
            'number_of_pickers': _('How many people are you?'),
        }

    first_name = forms.CharField(
        label=_("First name")
    )
    last_name = forms.CharField(
        label=_("Last name")
    )
    email = forms.EmailField(
        label=_("Email"),
        help_text=_("Enter a valid email address, please.")
    )
    phone = forms.CharField(
        label=_("Phone number")
    )
    comment = forms.CharField(
        label=_("Comments"),
        required=False,
        widget=forms.widgets.Textarea()
    )

    def __init__(self, *args, **kwargs):
        self.harvest = kwargs.pop('harvest')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']

        if AuthUser.objects.filter(email=email).exists():
            auth_user = AuthUser.objects.get(email=email)

            # check if a request with the same email already exists
            if RFP.objects.filter(person=auth_user.person, harvest_id=self.harvest.id).exists():
                raise forms.ValidationError(
                    _("You have already requested to join this pick.")
                )

        return email

    def save(self):
        instance = super().save(commit=False)
        instance.harvest = self.harvest

        # check if a user with the same email is already registered
        email = self.cleaned_data['email']
        if AuthUser.objects.filter(email=email).exists():
            auth_user = AuthUser.objects.get(email=email)
            instance.person = auth_user.person
        else:
            instance.person = Person.objects.create(
                first_name=self.cleaned_data['first_name'],
                family_name=self.cleaned_data['last_name'],
                phone=self.cleaned_data['phone'],
            )
            auth_user = AuthUser.objects.create(
                email=email,
                person=instance.person
            )

            group, __ = Group.objects.get_or_create(name='volunteer')
            auth_user.groups.add(group)

        instance.save()

        Email(
            recipient=instance.harvest.pick_leader.person,
            type=EmailType.NEW_HARVEST_RFP,
            harvest=instance.harvest,
        ).send(data=dict(EmailRFPSerializer(instance).data))

        return instance


class RFPManageForm(forms.ModelForm):
    """Pickleader RFP edit form."""

    class Meta:
        model = RFP
        fields = ['status', 'notes', 'send_email', 'email_body']
        widgets = {
            'status': forms.RadioSelect(),
            'notes': forms.widgets.Textarea(),
        }

    send_email = forms.BooleanField(
        label=_("Send confirmation email"),
        required=False,
        widget=forms.widgets.HiddenInput()
    )

    email_body = forms.CharField(
        label=_("Message to requester"),
        required=False,
        widget=forms.widgets.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        status = kwargs.pop('status')
        emailType = kwargs.pop('emailType')
        super().__init__(*args, **kwargs)

        if status in RFP.get_status_choices():
            self.fields['status'].widget = forms.widgets.HiddenInput()
            self.initial['status'] = status

        if emailType is not None:
            self.fields['send_email'].widget = forms.widgets.CheckboxInput()
            self.fields['email_body'].widget = forms.widgets.Textarea()
            harvest = self.instance.harvest
            self.email = Email(
                recipient=self.instance.person,
                type=emailType,
                harvest=harvest
            )
            self.initial['send_email'] = True
            self.initial['email_body'] = \
                self.email.get_default_message(self.email.harvest_data)

    def clean(self):
        status = self.cleaned_data.get('status')
        if status == RFP.Status.ACCEPTED and \
           status != self.instance.status and \
           self.instance.harvest.has_enough_pickers():
            raise forms.ValidationError(
                _("Enough pickers have already been accepted for this harvest. \
                To accept more, increase the number of required pickers first.")
            )

    def save(self):
        if self.cleaned_data.get('send_email'):
            email_body = self.cleaned_data.get('email_body')
            self.email.send(email_body)

        return super().save()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    content = forms.CharField(
        label=_("Pickleader notes"),
        required=False,
        widget=forms.widgets.Textarea(
            attrs={'placeholder': _("Your comment here")}
        )
    )


class PropertyForm(forms.ModelForm):
    """Property base form."""

    class Meta:
        model = Property
        exclude = [
            'longitude', 'latitude', 'geom',
            'pending_contact_first_name', 'pending_contact_family_name',
            'pending_contact_phone', 'pending_contact_email',
            'pending_recurring', 'pending_newsletter',
            'changed_by',
        ]
        widgets = {
            'owner': autocomplete.ModelSelect2('owner-autocomplete'),
            'trees': autocomplete.ModelSelect2Multiple('tree-autocomplete'),
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

    field_order = ['pending', 'is_active', 'authorized', 'owner']


class PropertyCreateForm(PropertyForm):
    """Property create form."""

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
                    _("You must either select an Owner \
                    or create a new one and provide their personal information"))
        return data

    def save(self):
        instance = super(PropertyCreateForm, self).save()
        person = Person.objects.create(
            first_name=self.cleaned_data['owner_first_name'],
            family_name=self.cleaned_data['owner_last_name'],
            phone=self.cleaned_data['owner_phone']
        )
        auth_user = AuthUser.objects.create(
            email=self.cleaned_data['owner_email'],
            person=person
        )
        auth_user.set_roles(['owner'])

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
            # 'public_access',
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
        label=_("Volunteers have permission to go on the neighbours' property to access fruits"),
        required=False,
    )

    compost_bin = forms.BooleanField(
        label=_('I have a compost bin where you can leave rotten fruit'),
        required=False,
    )

    ladder_available = forms.BooleanField(
        label=_('I have a ladder that can be used during the harvest'),
        required=False,
    )

    ladder_available_for_outside_picks = forms.BooleanField(
        label=_('I would lend my ladder for another harvest nearby'),
        required=False,
    )

    harvest_every_year = forms.BooleanField(
        label=_('My tree(s)/vine(s) produce fruit every year \
(if not, please include info about frequency in additional comments at the bottom)'),
        required=False,
    )

    pending_recurring = forms.ChoiceField(
        label=_('Have you provided us any information about your property before?'),
        choices=[(True, _('Yes')), (False, _('No'))],
        widget=forms.RadioSelect,
    )

    authorized = forms.ChoiceField(
        label=_('Do you give us permission to harvest your tree(s) and/or vine(s) this season?'),
        choices=[(True, _('Yes')), (False, _('Not this year, but maybe in future seasons'))],
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
        help_text=_('Any info on how to access the tree(s) or vine(s) \
(e.g. locked gate in back, publicly accessible from sidewalk, etc.)'),
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
        label=_('I would like to receive emails from \
Les Fruits Defendus such as newsletters and updates'),
        required=False
    )

    additional_info = forms.CharField(
        help_text=_('Any additional information that we should be aware of \
(e.g. details about how often tree produces fruit, description of fruit if \
the type is unknown or not in the list, etc.)'),
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
        cleaned_data = super().clean()
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
            'property': autocomplete.ModelSelect2(
                'property-autocomplete'
            ),
            'trees': autocomplete.ModelSelect2Multiple(
                url='tree-autocomplete',
                forward=['property']
            ),
            'pick_leader': autocomplete.ModelSelect2(
                'pickleader-autocomplete'
            ),
            'nb_required_pickers': forms.NumberInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("TREE queryset here>>> ", self.fields['trees'].queryset)

    start_date = forms.DateTimeField(
        label=_('Start date/time'),
        input_formats=['%d/%m/%Y %H:%M'],
        required=True
    )

    end_date = forms.DateTimeField(
        label=_('End time'),
        input_formats=['%H:%M'],
        required=True
    )

    publication_date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M', '%d/%m/%Y %H:%M:%S'],
        label=_("Publication date (optional)"),
        help_text=_("Leave this field empty to publish harvest as soon as possible"),
        required=False
    )

    def clean_end_date(self):
        """Derive end date from start date"""
        start = self.cleaned_data['start_date']
        end = self.cleaned_data['end_date']

        start_dt = start
        end_dt = dt.combine(start.date(), end.time(), tzinfo=start.tzinfo)

        if end_dt <= start_dt:
            raise forms.ValidationError(
                _('End time must be after start time')
            )

        return end_dt

    def clean_trees(self):
        """Make sure selected trees are registered on property"""
        property = self.cleaned_data['property']
        invalid_trees = []
        for tree in self.cleaned_data['trees']:
            if tree not in property.trees.all():
                invalid_trees.append(f"{tree.name_fr} ({tree.name_en})")
        if invalid_trees:
            raise forms.ValidationError(
                _('Selected tree(s) <{}> not registered on the selected property.')
                .format("; ".join(invalid_trees))
            )

    def clean_about(self):
        """Make sure announcement is filled before publishing"""
        status = self.cleaned_data['status']
        if status not in [
                Harvest.Status.ORPHAN,
                Harvest.Status.PENDING,
                Harvest.Status.CANCELLED
        ]:
            if not self.cleaned_data['about']:
                raise forms.ValidationError(
                    _('Please fill in the public announcement to be published on the calendar.')
                )


    def clean(self):
        """Make sure pick_leader and status fields are compatible"""
        data = super().clean()

        if data['status'] == Harvest.Status.ORPHAN:
            unresolved_requests = self.instance.requests.filter(
                status__in=[RFP.Status.PENDING, RFP.Status.ACCEPTED]
            )
            if unresolved_requests.exists():
                raise forms.ValidationError(
                    _("This harvest can't be left orphan, resolve requests first.")
                )

            if data['pick_leader'] is not None:
                data['status'] = Harvest.Status.ADOPTED

        if data['pick_leader'] is None and data['status'] not in [
                Harvest.Status.ORPHAN,
                Harvest.Status.PENDING,
                Harvest.Status.CANCELLED,
        ]:
            raise forms.ValidationError(
                _("You must choose a pick leader or change harvest status")
            )

        return data


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
    """Equipment form."""

    class Meta:
        model = Equipment
        fields = ['owner', 'type', 'description', 'count']
        widgets = {
            'owner': autocomplete.ModelSelect2(
                'equipmentpoint-autocomplete',
            ),
        }
        labels = {
            'owner': _('Equipment Point'),
        }
