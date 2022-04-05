# coding: utf-8

from django.db import models
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import ( Group, AbstractBaseUser,
                                         PermissionsMixin, BaseUserManager )
from django.core.validators import RegexValidator
from phone_field import PhoneField
from harvest.models import RequestForParticipation, Harvest, Property

AUTH_GROUPS = (
    ('core', _("Core Member")),
    ('pickleader', _("Pick Leader")),
    ('volunteer', _("Volunteer Picker")),
    ('owner', _("Property Owner")),
    ('contact', _("Contact Person")),
)

STAFF_GROUPS = ['core', 'pickleader']

class AuthUserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

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
        user.save(using=self._db)
        return user


class AuthUser(AbstractBaseUser, PermissionsMixin):

    person = models.OneToOneField(
        'Person',
        on_delete=models.CASCADE,
        null=True,
        related_name='auth_user'
    )

    alphanumeric = RegexValidator(
        r'^[0-9a-zA-Z]*$',
        message='Only alphanumeric characters are allowed.'
    )

    # Redefine the basic fields that would normally be defined in User
    email = models.EmailField(
        verbose_name='email address',
        unique=True,
        max_length=255
    )

    # Our own fields
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, null=False)
    is_staff = models.BooleanField(default=False, null=False)

    objects = AuthUserManager()
    USERNAME_FIELD = 'email'

    def set_roles(self, roles):
        ''' updates user's groups
            :param roles: list of group names (see AUTH_GROUPS)
        '''
        self.groups.clear()
        for role in roles:
            group, __ =  Group.objects.get_or_create(name=role)
            self.groups.add(group)

        self.is_staff = any([r in STAFF_GROUPS for r in roles])
        self.save()

    @property
    def role_groups(self):
        ''' return user's role groups'''
        return self.groups.filter(name__in=[t[0] for t in AUTH_GROUPS])

    @property
    def roles(self):
        ''' lists user's role names'''
        return [dict(AUTH_GROUPS).get(g.name) for g in self.role_groups]

    def __str__(self):
        if self.person:
            return u"%s" % self.person
        else:
            return self.email


class Actor(models.Model):
    actor_id = models.AutoField(
        primary_key=True
    )

    class Meta:
        verbose_name = _("actor")
        verbose_name_plural = _("actors")

    def get_person(self):
        return Person.objects.filter(actor_id=self.actor_id).first()

    def get_organization(self):
        return Organization.objects.filter(actor_id=self.actor_id).first()

    @property
    def is_person(self):
        if self.get_person():
            return True
        return False

    @property
    def is_organization(self):
        if self.get_organization():
            return True
        return False

    def __str__(self):
        if self.is_person:
            return self.get_person().__str__()
        elif self.is_organization:
            return self.get_organization().__str__()
        else:
            return u"Unknown Actor: %i" % self.actor_id


class Person(Actor):
    redmine_contact_id = models.IntegerField(
        verbose_name=_("Redmine contact"),
        null=True,
        blank=True
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
        verbose_name=_("Neighborhood"),
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

    language = models.ForeignKey(
        'member.Language',
        null=True,
        blank=True,
        verbose_name=_("Preferred language"),
        on_delete=models.CASCADE,
    )

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True
    )

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("people")
        ordering = ["first_name"]

    def __str__(self):
        return u"%s %s" % (self.first_name, self.family_name)

    def name(self):
        return u"%s %s" % (self.first_name, self.family_name)

    def email(self):
        auth_obj = AuthUser.objects.filter(person=self)
        if auth_obj:
            return auth_obj[0].email
        else:
            return None

    @property
    def properties(self):
        # TODO set up reverse relationship instead
        return Property.objects.filter(owner=self)

    @property
    def harvests_as_pickleader(self):
        return Harvest.objects.filter(pick_leader=self.auth_user)

    @property
    def requests_as_volunteer(self):
        return RequestForParticipation.objects.filter(picker=self)

    @property
    def harvests_as_volunteer_accepted(self):
        requests = self.requests_as_volunteer.filter(is_accepted=True)
        return Harvest.objects.filter(request_for_participation__in=requests)

    @property
    def harvests_as_volunteer_pending(self):
        requests = self.requests_as_volunteer.exclude(Q(is_accepted=True)|Q(is_cancelled=True))
        return Harvest.objects.filter(request_for_participation__in=requests)

    @property
    def harvests_as_volunteer_missed(self):
        requests = self.requests_as_volunteer.filter(Q(is_accepted=False)|Q(is_cancelled=True))
        return Harvest.objects.filter(request_for_participation__in=requests)

    @property
    def harvests_as_owner(self):
        return Harvest.objects.filter(property__in=self.properties)


class Organization(Actor):
    is_beneficiary = models.BooleanField(
        verbose_name=_('is beneficiary'),
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
        verbose_name=_("Description"),
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
        on_delete=models.CASCADE,
    )

    contact_person_role = models.CharField(
        verbose_name=_("Contact person role"),
        max_length=50,
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
        verbose_name=_("Neighborhood"),
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


    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
        ordering = ["civil_name"]

    def __str__(self):
        return u"%s" % self.civil_name

    def name(self):
        return u"%s" % self.civil_name
    
    def email(self):
        return self.contact_person.email()

class Neighborhood(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=150
    )

    class Meta:
        verbose_name = _("neighborhood")
        verbose_name_plural = _("neighborhoods")

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=150
    )

    class Meta:
        verbose_name = _("city")
        verbose_name_plural = _("cities")

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=150
    )

    class Meta:
        verbose_name = _("state")
        verbose_name_plural = _("states")

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=150
    )

    class Meta:
        verbose_name = _("country")
        verbose_name_plural = _("countries")

    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=150
    )

    class Meta:
        verbose_name = _("language")
        verbose_name_plural = _("languages")

    def __str__(self):
        return self.name
