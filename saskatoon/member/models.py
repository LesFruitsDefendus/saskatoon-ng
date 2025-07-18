import re
from django.core.cache import cache
from django.contrib.auth.models import (
    Group,
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone as tz
from itertools import chain
from operator import attrgetter
from phone_field import PhoneField
from typing import Optional, Any, Tuple

from harvest.models import (
    RequestForParticipation as RFP,
    Harvest,
)


# type aliases to satisfy pytype
HarvestStatus = Optional[Tuple[Any, str]]  # Optional[Harvest.Status]
RFPStatus = Optional[Tuple[Any, str]]  # Optional[RFP.Status]


class AuthUserManager(BaseUserManager):
    """Base user management"""

    def create_user(self, email, password=None):
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(email=self.normalize_email(email),
                          )
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.add_role('admin')
        user.save(using=self._db)
        return user


class AuthUser(AbstractBaseUser, PermissionsMixin):
    """Base user model"""

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["date_joined"]

    GROUPS = (
        ('core', _("Core Member")),
        ('pickleader', _("Pick Leader")),
        ('volunteer', _("Volunteer Picker")),
        ('owner', _("Property Owner")),
        ('contact', _("Contact Person")),
    )

    STAFF_GROUPS = ['core', 'pickleader']

    person = models.OneToOneField(
        'Person',
        on_delete=models.CASCADE,
        null=True,
        related_name='auth_user'
    )

    has_temporary_password = models.BooleanField(
        default=False,
        null=False
    )

    agreed_terms = models.BooleanField(
        default=False,
        null=False
    )

    # AbstractBaseUser fields #
    email = models.EmailField(
        verbose_name=_('email address'),
        unique=True,
        max_length=255
    )
    objects = AuthUserManager()
    USERNAME_FIELD = 'email'
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, null=False)
    is_staff = models.BooleanField(default=False, null=False)

    def add_role(self, role, commit=True):
        ''' add role to user
            :param role: AuthUser.GROUP name
        '''
        group, _ = Group.objects.get_or_create(name=role)
        self.groups.add(group)
        if commit:
            self.save()

    def set_roles(self, roles):
        ''' updates user's groups
            :param roles: list of AuthUser.GROUP names
        '''
        self.groups.clear()
        for role in roles:
            self.add_role(role, False)

        self.is_staff = any([r in self.STAFF_GROUPS for r in roles])
        self.save()

    @property
    def role_groups(self):
        ''' returns user's role groups'''
        return self.groups.filter(name__in=[t[0] for t in self.GROUPS])

    @property
    def roles(self):
        ''' lists user's role names'''
        return [dict(self.GROUPS).get(g.name) for g in self.role_groups]

    @property
    def is_onboarding(self):
        ''' whether the user has yet to go through the onboarding flow
            (i.e. an authenticated user that has a volunteer role) '''
        group_names = [g.name for g in self.role_groups]
        return ('pickleader' not in group_names and
                'volunteer' in group_names and
                self.has_temporary_password)

    @property
    def name(self):
        if self.person is not None:
            return self.person.name
        return None

    def __str__(self):
        if self.person:
            return u"%s" % self.person
        else:
            return self.email


class Onboarding(models.Model):
    """Pickleader Registration"""

    class Meta:
        verbose_name = _("user onboarding")
        verbose_name_plural = _("user onboarding")

    name = models.CharField(
        verbose_name=_("Reference name"),
        max_length=50,
        default="",
    )

    datetime = models.DateTimeField(auto_now_add=True)

    all_sent = models.BooleanField(
        verbose_name=_('All invites sent'),
        default=False
    )

    log = models.TextField(
        blank=True,
        default=""
    )

    @property
    def user_count(self):
        return self.persons.count()

    def __str__(self):
        return "{} [{}]".format(
            self.name,
            tz.localtime(self.datetime).strftime("%B %d, %Y @ %-I:%M %p")
        )


class Actor(models.Model):
    """Actor (Person or Organization)"""

    class Meta:
        verbose_name = _("actor")
        verbose_name_plural = _("actors")

    actor_id = models.AutoField(
        primary_key=True
    )

    @property
    def is_person(self):
        return hasattr(self, 'person')

    @property
    def is_organization(self):
        return hasattr(self, 'organization')

    def get_person(self):
        if self.is_person:
            return self.person
        return Person.objects.none()

    def get_organization(self):
        if self.is_organization:
            return self.organization
        return Organization.objects.none()

    def __str__(self):
        if self.is_person:
            return self.get_person().__str__()
        elif self.is_organization:
            return self.get_organization().__str__()
        else:
            return u"Unknown Actor: %i" % self.actor_id


class Person(Actor):
    """Person model"""

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("persons")
        ordering = ["first_name"]

    class Language(models.TextChoices):
        FR = 'fr', "Français"
        EN = 'en', "English"

    language = models.CharField(
        verbose_name=_("Preferred Language"),
        max_length=2,
        choices=Language.choices,
        default=Language.FR,
    )

    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=30
    )

    family_name = models.CharField(
        verbose_name=_("Family name"),
        max_length=50,
        null=True,
        blank=True
    )

    phone = PhoneField(
        verbose_name=_("Phone"),
        null=True,
        blank=True
    )

    street_number = models.CharField(
        verbose_name=_("Number"),
        max_length=10,
        null=True,
        blank=True
    )

    street = models.CharField(
        verbose_name=_("Street"),
        max_length=50,
        null=True,
        blank=True
    )

    complement = models.CharField(
        verbose_name=_("Complement"),
        max_length=150,
        null=True,
        blank=True
    )

    postal_code = models.CharField(
        verbose_name=_("Postal code"),
        max_length=10,
        null=True,
        blank=True
    )

    neighborhood = models.ForeignKey(
        'Neighborhood',
        verbose_name=_("Borough"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    city = models.ForeignKey(
        'City',
        verbose_name=_("City"),
        null=True,
        default=1,
        on_delete=models.CASCADE,
    )

    state = models.ForeignKey(
        'State',
        verbose_name=_("State"),
        null=True,
        default=1,
        on_delete=models.CASCADE,
    )

    country = models.ForeignKey(
        'Country',
        verbose_name=_("Country"),
        null=True,
        default=1,
        on_delete=models.CASCADE,
    )

    newsletter_subscription = models.BooleanField(
        verbose_name=_('Newsletter subscription'),
        default=False
    )

    longitude = models.FloatField(
        verbose_name=_("Longitude"),
        null=True,
        blank=True
    )

    latitude = models.FloatField(
        verbose_name=_("Latitude"),
        null=True,
        blank=True
    )

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True
    )

    onboarding = models.ForeignKey(
        'Onboarding',
        related_name="persons",
        on_delete=models.SET_NULL,
        verbose_name=_('Onboarding group'),
        null=True,
        blank=True
     )

    def __str__(self):
        return u"%s %s" % (self.first_name, self.family_name)

    @property
    def name(self):
        return u"%s %s" % (self.first_name, self.family_name)

    @property
    def email(self):
        if not hasattr(self, 'auth_user') or self.auth_user is None:
            return None
        return self.auth_user.email

    @property
    def comment_emails(self):
        """Look for emails in comments"""
        EMAIL_PATTERN = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"  # noqa: W605
        matches = re.findall(EMAIL_PATTERN, self.comments)
        return matches

    def get_organizations_as_contact(self):
        return Organization.objects.filter(contact_person=self)

    def get_harvests_as_owner(self, status: HarvestStatus = None):
        harvests = Harvest.objects.filter(
            property__in=self.properties.all()
        ).annotate(role=models.Value('owner'))
        if status is not None:
            return harvests.filter(status=status)
        return harvests

    def get_harvests_as_pickleader(self, status: HarvestStatus = None):
        if not hasattr(self, 'auth_user'):
            return Harvest.objects.none()
        harvests = self.auth_user.harvests.annotate(role=models.Value('pickleader'))
        if status is not None:
            return harvests.filter(status=status)
        return harvests

    def get_requests_as_volunteer(self, rfp_status: RFPStatus = None):
        rfps = self.requests.filter(harvest__status=Harvest.Status.SUCCEEDED)
        if rfp_status is not None:
            return rfps.filter(status=rfp_status)
        return rfps

    def get_harvests_as_volunteer(self):
        harvests = Harvest.objects.filter(
            status=Harvest.Status.SUCCEEDED,
            requests__in=self.requests.all()
        )
        return list(chain.from_iterable([
            harvests.filter(
                requests__in=self.requests.filter(status=s)
            ).annotate(
                rfp_status=models.Value(s),
                role=models.Value('volunteer'),
            )
            for s in [
                RFP.Status.ACCEPTED,
                RFP.Status.DECLINED,
                RFP.Status.CANCELLED,
            ]
        ]))

    def get_harvests(self):
        return sorted(
            chain(
                self.get_harvests_as_owner(),
                self.get_harvests_as_pickleader(),
                self.get_harvests_as_volunteer(),
            ),
            key=attrgetter('start_date'),
            reverse=True,
        )

    @property
    def accept_count(self):
        return self.get_requests_as_volunteer(RFP.Status.ACCEPTED).count()

    @property
    def reject_count(self):
        return self.get_requests_as_volunteer(RFP.Status.DECLINED).count()


class Organization(Actor):
    """Organization model"""

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
        ordering = ["civil_name"]

    is_beneficiary = models.BooleanField(
        verbose_name=_('Is Beneficiary'),
        help_text=_(
            'Only check this box if the Organization is currently accepting fruit donations'
        ),
        default=False
    )

    is_equipment_point = models.BooleanField(
        verbose_name=_('Is Equipment Point'),
        help_text=_(
            'Only check this box if the equipment registered at this Organization \
is currenlty made available'
        ),
        default=False
    )

    redmine_contact_id = models.IntegerField(
        verbose_name=_("Redmine contact"),
        null=True,
        blank=True
    )

    civil_name = models.CharField(
        verbose_name=_("Name"),
        max_length=50
    )

    description = models.TextField(
        verbose_name=_("Short description"),
        blank=True
    )

    beneficiary_description = models.TextField(
        verbose_name=_("Beneficiary description"),
        blank=True
    )

    equipment_description = models.TextField(
        verbose_name=_("Equipment point description"),
        blank=True
    )

    phone = PhoneField(
        verbose_name=_("Phone"),
        null=True
    )

    contact_person = models.ForeignKey(
        'Person',
        null=True,
        verbose_name=_("Contact person"),
        on_delete=models.SET_NULL,
    )

    contact_person_role = models.CharField(
        verbose_name=_("Contact person role"),
        max_length=50,
        null=True,
        blank=True
    )

    street_number = models.CharField(
        verbose_name=_("Street number"),
        max_length=10,
        null=True,
        blank=True
    )

    street = models.CharField(
        verbose_name=_("Street"),
        max_length=50,
        null=True,
        blank=True
    )

    complement = models.CharField(
        verbose_name=_("Complement"),
        max_length=150,
        null=True,
        blank=True
    )

    postal_code = models.CharField(
        verbose_name=_("Postal code"),
        max_length=10,
        null=True,
        blank=True
    )

    neighborhood = models.ForeignKey(
        'Neighborhood',
        verbose_name=_("Borough"),
        null=True,
        on_delete=models.CASCADE,
    )

    city = models.ForeignKey(
        'City',
        verbose_name=_("City"),
        null=True,
        default=1,
        on_delete=models.CASCADE,
    )

    state = models.ForeignKey(
        'State',
        verbose_name=_("State"),
        null=True,
        default=1,
        on_delete=models.CASCADE,
    )

    country = models.ForeignKey(
        'Country',
        verbose_name=_("Country"),
        null=True,
        default=1,
        on_delete=models.CASCADE,
    )

    longitude = models.FloatField(
        verbose_name=_("Longitude"),
        null=True,
        blank=True,
    )

    latitude = models.FloatField(
        verbose_name=_("Latitude"),
        null=True,
        blank=True
    )

    @property
    def short_address(self):
        if self.street_number and self.street and self.complement:
            return "%s %s, %s" % (
                self.street_number,
                self.street,
                self.complement
            )
        elif self.street and self.street_number:
            return "%s %s" % (
                self.street_number,
                self.street
            )
        elif self.street and self.complement:
            return "%s, %s" % (
                self.street,
                self.complement
            )
        else:
            return self.street

    @property
    def address(self):
        if self.city and self.state and self.postal_code:
            return "%s. %s %s, %s" % (
                self.short_address,
                self.city,
                self.state,
                self.postal_code
            )
        elif self.city:
            return "%s. %s" % (
                self.short_address,
                self.city,
            )
        return self.short_address

    def __str__(self):
        return u"%s" % self.civil_name

    @property
    def name(self):
        return u"%s" % self.civil_name

    @property
    def contact(self):
        return self.contact_person.name if self.contact_person else None

    @property
    def email(self):
        return self.contact_person.email if self.contact_person else None

    @property
    def language(self):
        if self.contact_person is not None:
            return self.contact_person.language
        return Person.Language.FR


class Neighborhood(models.Model):
    """Borough model"""

    class Meta:
        verbose_name = _("borough")
        verbose_name_plural = _("boroughs")
        ordering = ["name"]

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=150
    )

    def __str__(self):
        return self.name


class City(models.Model):
    """City model"""

    class Meta:
        verbose_name = _("city")
        verbose_name_plural = _("cities")

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=150
    )

    def __str__(self):
        return self.name


class State(models.Model):
    """State model"""

    class Meta:
        verbose_name = _("state")
        verbose_name_plural = _("states")
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=150
    )

    def __str__(self):
        return self.name


class Country(models.Model):
    """Country model"""

    class Meta:
        verbose_name = _("country")
        verbose_name_plural = _("countries")

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=150
    )

    def __str__(self):
        return self.name


# CACHE #

@receiver(post_save, sender=Person)
def clear_cache_people(sender, instance, **kwargs):
    cache.delete_pattern("*person*")


@receiver(post_save, sender=Organization)
def clear_cache_organization(sender, instance, **kwargs):
    cache.delete_pattern("*organization*")
