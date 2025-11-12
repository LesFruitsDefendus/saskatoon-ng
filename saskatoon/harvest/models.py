from crequest.middleware import CrequestMiddleware
from datetime import datetime
from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator
from django_quill.fields import QuillField
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone as tz
from djgeojson.fields import PointField
from phone_field import PhoneField
from typing import Optional
from enum import Enum

from sitebase.utils import local_datetime, to_datetime, is_quill_html_empty


class TreeType(models.Model):
    """Tree Type model"""

    class Meta:
        verbose_name = _("tree type")
        verbose_name_plural = _("tree types")
        ordering = ["name_en"]

    name_en = models.CharField(
        verbose_name=_("Tree name (en)"),
        max_length=20,
        default=""
    )

    name_fr = models.CharField(
        verbose_name=_("Nom de l'arbre (fr)"),
        max_length=20,
        default=""
    )

    fruit_name_en = models.CharField(
        verbose_name=_("Fruit name (en)"),
        max_length=20,
        default=""
    )

    fruit_name_fr = models.CharField(
        verbose_name=_("Nom du fruit (fr)"),
        max_length=20,
        default=""
    )

    fruit_icon = models.CharField(
        verbose_name=_("Fruit icon"),
        max_length=50,
        blank=True,
        null=True,
    )

    maturity_start = models.DateField(
        verbose_name=_("Maturity start date"),
        blank=True,
        null=True
    )

    maturity_end = models.DateField(
        verbose_name=_("Maturity end date"),
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='fruits_images',
        verbose_name=_("Fruit image"),
        blank=True,
        null=True
    )

    def get_name(self, lang='fr'):
        return getattr(self, "name_{}".format(lang))

    def get_fruit_name(self, lang='fr'):
        return getattr(self, "fruit_name_{}".format(lang))

    @property
    def maturity_range(self):
        return "{} - {}".format(
            self.maturity_start.strftime("%b. %-d"),
            self.maturity_end.strftime("%b. %-d, %Y"),
        )

    @property
    def fruit(self):
        return "{} / {}".format(self.fruit_name_fr, self.fruit_name_en)

    @property
    def name(self):
        return "{} / {}".format(self.name_fr, self.name_en)

    def __str__(self):
        return self.name


@receiver(pre_save, sender=TreeType)
def update_orphan_harvests(sender, instance, **kwargs):
    try:
        original = TreeType.objects.get(id=instance.id)

        if (original.maturity_start != instance.maturity_start or
                original.maturity_end != instance.maturity_end):

            Harvest.objects.filter(
                status=Harvest.Status.ORPHAN,
                start_date__year=tz.now().date().year,
                trees=instance,
            ).update(
                start_date=to_datetime(instance.maturity_start),
                end_date=to_datetime(instance.maturity_end)
            )
    except TreeType.DoesNotExist:
        pass


class EquipmentType(models.Model):
    """Equipment Type model"""

    class Meta:
        verbose_name = _("equipment type")
        verbose_name_plural = _("equipment types")

    name_fr = models.CharField(
        verbose_name=_("Nom (fr)"),
        max_length=50
    )

    name_en = models.CharField(
        verbose_name=_("Name (en)"),
        max_length=50,
        default="",
    )

    def get_name(self, lang='fr'):
        return getattr(self, "name_{}".format(lang))

    def __str__(self):
        return "{} / {}".format(self.name_fr, self.name_en)


class Property(models.Model):
    """ Property model"""

    class Meta:
        verbose_name = _("property")
        verbose_name_plural = _("properties")
        ordering = ['-id',]

    owner = models.ForeignKey(
        'member.Actor',
        null=True,
        blank=True,
        verbose_name=_("Owner"),
        related_name='properties',
        on_delete=models.CASCADE,
    )

    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        help_text=_("This property exists and may be able to host a pick"),
        default=True
    )

    authorized = models.BooleanField(
        verbose_name=_("Authorized for this season"),
        help_text=_(
            "Harvest in this property has been authorized for the current season by its owner"
        ),
        null=True,
        default=None
    )

    pending = models.BooleanField(
        verbose_name=_("Pending"),
        help_text=_("This property was created through a public form \
and needs to be validated by an administrator"),
        default=True
    )

    pending_contact_first_name = models.CharField(
        blank=True,
        verbose_name=_("Contact first name"),
        help_text=_("First name of the person to be contacted for confirmation"),
        max_length=50
    )

    pending_contact_family_name = models.CharField(
        blank=True,
        verbose_name=_("Contact family name"),
        help_text=_("Family name of the person to be contacted for confirmation"),
        max_length=50
    )

    pending_contact_phone = PhoneField(
        blank=True,
        verbose_name=_("Contact phone number"),
        help_text=_("Phone number to be used for confirmation"),
    )

    pending_contact_email = models.EmailField(
        verbose_name=_("Contact email"),
        help_text=_("Email address to be used for confirmation"),
        null=True,
        blank=True,
    )

    pending_newsletter = models.BooleanField(
        verbose_name=_("Newsletter subscription"),
        default=False
    )

    pending_recurring = models.BooleanField(
        verbose_name=_("Recurring property signup"),
        default=False
    )

    geom = PointField(null=True, blank=True)

    trees: models.ManyToManyField[TreeType, models.Model] = models.ManyToManyField(
        'TreeType',
        verbose_name=_("Fruit tree/vine type(s)"),
        help_text=_(
            'Select multiple fruit types if applicable. \
Unknown fruit type or colour can be mentioned in the additional comments at the bottom.'
        ),
    )

    trees_location = models.CharField(
        verbose_name=_("Trees location"),
        help_text=_("Front yard or backyard?"),
        null=True,
        blank=True,
        max_length=200
    )

    trees_accessibility = models.CharField(
        verbose_name=_("Trees accessibility"),
        help_text=_("Any info on how to access the tree (eg. key, gate etc)"),
        null=True,
        blank=True,
        max_length=200
    )

    avg_nb_required_pickers = models.PositiveIntegerField(
        verbose_name=_("Required pickers on average"),
        null=True,
        default=1
    )

    public_access = models.BooleanField(
        verbose_name=_("Publicly accessible"),
        default=False,
    )

    neighbor_access = models.BooleanField(
        verbose_name=_("Access to neighboring terrain if needed"),
        default=False,
    )

    compost_bin = models.BooleanField(
        verbose_name=_("Compost bin closeby"),
        default=False,
    )

    ladder_available = models.BooleanField(
        verbose_name=_("There is a ladder available in the property"),
        default=False,
    )

    ladder_available_for_outside_picks = models.BooleanField(
        verbose_name=_(
            "A ladder is available in the property and can be used for nearby picks"
        ),
        default=False,
    )

    harvest_every_year = models.BooleanField(
        verbose_name=_("Produces fruits every year"),
        default=False,
    )

    number_of_trees = models.PositiveIntegerField(
        verbose_name=_("Total number of trees/vines on this property"),
        blank=True,
        null=True
    )

    approximative_maturity_date = models.DateField(
        verbose_name=_("Approximative maturity date"),
        help_text=_("When is the tree commonly ready to be harvested?"),
        blank=True,
        null=True
    )

    fruits_height = models.PositiveIntegerField(
        verbose_name=_("Height of lowest fruits (meters)"),
        blank=True,
        null=True
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

    publishable_location = models.CharField(
        verbose_name=_("Publishable location"),
        help_text=_(
            "Aproximative location to be used in public communications (not the actual address)"
        ),
        max_length=50,
        null=True,
        blank=True
    )

    neighborhood = models.ForeignKey(
        'member.Neighborhood',
        verbose_name=_("Borough"),
        null=True,
        on_delete=models.CASCADE,
    )

    city = models.ForeignKey(
        'member.City',
        verbose_name=_("City"),
        null=True,
        default=1,
        on_delete=models.CASCADE,
    )

    state = models.ForeignKey(
        'member.State',
        verbose_name=_("Province"),
        null=True,
        default=1,
        on_delete=models.CASCADE,
    )

    country = models.ForeignKey(
        'member.Country',
        verbose_name=_("Country"),
        null=True,
        default=1,
        on_delete=models.CASCADE,
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

    additional_info = models.CharField(
        verbose_name=_("Additional information"),
        help_text=_("Any additional information that we should be aware of"),
        max_length=1000,
        null=True,
        blank=True
    )

    changed_by = models.ForeignKey(
        'member.AuthUser',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
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
    def last_succeeded_harvest_date(self):
        """Date of the last successful harvest for this property"""
        last_harvest = self.harvests\
                           .filter(status=Harvest.Status.SUCCEEDED)\
                           .order_by('start_date').last()
        return last_harvest.start_date if last_harvest else None

    def get_owner_subclass(self):
        if self.owner:
            if self.owner.is_person:
                return self.owner.person
            if self.owner.is_organization:
                return self.owner.organization
        return None

    @property
    def owner_email(self):
        owner_subclass = self.get_owner_subclass()
        return owner_subclass.email if owner_subclass else None

    @property
    def owner_phone(self):
        owner_subclass = self.get_owner_subclass()
        return owner_subclass.phone if owner_subclass else None

    @property
    def owner_name(self):
        if self.owner:
            return self.owner.__str__()
        return u"(%s %s)" % (self.pending_contact_first_name,
                             self.pending_contact_family_name)

    @property
    def email_recipient(self):
        if self.owner and self.owner.is_person:
            return self.owner.person
        elif self.owner and self.owner.is_organization:
            return self.owner.contact_person
        return None

    @property
    def pending_contact_name(self):
        if self.pending_contact_first_name and self.pending_contact_family_name:
            return " ".join([
                self.pending_contact_first_name,
                self.pending_contact_family_name,
            ])
        elif self.pending_contact_first_name:
            return self.pending_contact_first_name
        elif self.pending_contact_family_name:
            return self.pending_contact_family_name
        return ""

    @property
    def needs_orphan(self):
        if not self.authorized or self.pending:
            return False
        return self.trees.count() > \
            self.harvests.filter(start_date__year=tz.now().date().year).count()

    def __str__(self):
        number = self.street_number if self.street_number else ""
        return u"%s %s %s %s" % (self.owner_name, _("at"), number, self.street)


class Equipment(models.Model):
    """Equipment model"""

    class Meta:
        verbose_name = _("equipment")
        verbose_name_plural = _("equipment")

    type = models.ForeignKey(
        'EquipmentType',
        verbose_name=_("Type"),
        on_delete=models.CASCADE,
    )

    owner = models.ForeignKey(
        'member.Actor',
        verbose_name=_("Owner"),
        related_name="equipment",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    property = models.ForeignKey(
        'Property',
        verbose_name=_("Property"),
        related_name="equipment",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    description = models.CharField(
        verbose_name=_("Description"),
        max_length=50,
        blank=True
    )

    count = models.SmallIntegerField(
        verbose_name=_("Number available"),
        default=1
    )

    shared = models.BooleanField(
        verbose_name=_("Shared"),
        help_text=_("Can be used in harvests outside of property"),
        default=False
    )

    def get_equipment_point(self):
        if self.owner is not None and self.owner.is_organization:
            return self.owner.get_organization()
        return None

    def inventory(self, lang='fr'):
        return "%i %s" % (self.count, self.type.get_name(lang))

    def __str__(self):
        return "%s (%s)" % (self.description, self.type)

    def save(self, *args, **kwargs):
        if self.get_equipment_point() is not None:
            self.shared = True
        super().save(*args, **kwargs)


class Harvest(models.Model):
    """Harvest model"""

    class Meta:
        verbose_name = _("harvest")
        verbose_name_plural = _("harvests")
        ordering = ['-start_date']

    class Status(models.TextChoices, Enum):
        ORPHAN = 'orphan', _("Orphan")
        ADOPTED = 'adopted', _("Adopted")
        PENDING = 'pending', _("To be confirmed")
        SCHEDULED = 'scheduled', _("Scheduled")
        READY = 'ready', _("Ready")
        SUCCEEDED = 'succeeded', _("Succeeded")
        CANCELLED = 'cancelled', _("Cancelled")

    PUBLISHABLE_STATUSES = [
        Status.READY,
        Status.SCHEDULED,
        Status.SUCCEEDED
    ]

    SEASON_CHOICES = [
        (y, y) for y in range(datetime.now().year, 2015, -1)
    ]

    status = models.CharField(
        choices=Status.choices,
        max_length=20,
        verbose_name=_("Harvest status"),
        default=Status.ORPHAN,
    )

    # WARNING: conflicts with @property decorator :/
    property = models.ForeignKey(
        'Property',
        null=True,
        verbose_name=_("Property"),
        related_name='harvests',
        on_delete=models.CASCADE,
    )

    trees: models.ManyToManyField[TreeType, models.Model] = models.ManyToManyField(
        'TreeType',
        verbose_name=_("Fruit trees")
    )

    owner_present = models.BooleanField(
        verbose_name=_("Owner wants to be present"),
        default=False
    )

    owner_help = models.BooleanField(
        verbose_name=_("Owner wants to participate"),
        default=False
    )

    owner_fruit = models.BooleanField(
        verbose_name=_("Owner wants their share of fruits"),
        default=False
    )

    pick_leader = models.ForeignKey(
        'member.AuthUser',
        null=True,
        blank=True,
        verbose_name="Pick leader",
        related_name='harvests',
        on_delete=models.CASCADE,
    )

    start_date = models.DateTimeField(
        verbose_name=_("Start date"),
        blank=True,
        null=True
    )

    end_date = models.DateTimeField(
        verbose_name=_("End date"),
        blank=True,
        null=True
    )

    publication_date = models.DateTimeField(
        verbose_name=_("Publication date"),
        blank=True,
        null=True
    )

    equipment_reserved: models.ManyToManyField[Equipment, models.Model] = models.ManyToManyField(
        'Equipment',
        verbose_name=_("Reserve equipment"),
        blank=True
    )

    nb_required_pickers = models.PositiveIntegerField(
        verbose_name=_("Number of required pickers"),
        default=3
    )

    about = QuillField(
        verbose_name=_("Public announcement"),
        max_length=1000,
        help_text=_("Published on public facing calendar"),
        null=True,
        blank=True
    )

    changed_by = models.ForeignKey(
        'member.AuthUser',
        related_name='harvest_edited',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    date_created = models.DateTimeField(
        verbose_name=_("Creation date"),
        auto_now_add=True
    )

    def __str__(self):
        start = self.get_local_start()
        if start is not None:
            return _("Harvest on {} for {}").format(
                start.strftime("%d/%m/%Y %H:%M"),
                self.property
            )
        return _("Harvest for {}").format(self.property)

    @staticmethod
    def get_status_choices():
        """Pending status is no longer used"""
        return [s for s in Harvest.Status.choices
                if s[0] != Harvest.Status.PENDING]

    def get_total_distribution(self) -> Optional[int]:
        return self.yields.aggregate(
            models.Sum("total_in_lb")
        ).get("total_in_lb__sum")

    def get_local_start(self):
        return local_datetime(self.start_date)

    def get_local_end(self):
        return local_datetime(self.end_date)

    def get_date_range(self) -> str:
        start = self.get_local_start()
        end = self.get_local_end()
        if start is None or end is None or start.date() == end.date():
            return ""

        return "{} - {}".format(
            start.strftime("%b. %-d"),
            end.strftime("%b. %-d, %Y"),
        )

    def has_public_announcement(self) -> bool:
        return self.about is not None and not is_quill_html_empty(self.about.html)

    def get_local_publish_date(self):
        return local_datetime(self.publication_date)

    def get_volunteers_count(self, status: Optional['RequestForParticipation.Status']) -> int:
        rfps = self.requests.get_queryset()
        if status is not None:
            rfps = rfps.filter(status=status)

        if not rfps:
            return 0

        return rfps.aggregate(models.Sum('number_of_pickers')).get('number_of_pickers__sum', 0)

    def has_enough_pickers(self) -> bool:
        accepted = self.get_volunteers_count(RequestForParticipation.Status.ACCEPTED)
        return accepted >= self.nb_required_pickers

    def has_pending_requests(self) -> bool:
        return self.get_volunteers_count(RequestForParticipation.Status.PENDING) > 0

    def get_days_before_harvest(self):
        diff = datetime.now() - self.start_date
        return diff.days

    def get_neighborhood(self):
        return self.property.neighborhood.name

    def get_fruits(self):
        return [t.fruit for t in self.trees.all()]

    def get_public_title(self):
        title = ", ".join(self.get_fruits())
        if self.property.neighborhood.name != "Other":
            title += f" @ {self.property.neighborhood.name}"
        return title

    def is_urgent(self):
        if not self.start_date:
            return False

        days = self.get_days_before_harvest()
        return (
            (self.status is Harvest.Status.ORPHAN and days < 14) or
            (self.status is Harvest.Status.SCHEDULED and days < 3)
        )

    def is_publishable(self):
        if self.status not in self.PUBLISHABLE_STATUSES:
            return False
        if not self.publication_date:
            return True
        return (tz.now() > self.publication_date)

    def is_open_to_requests(self, public: bool = True):
        if self.end_date is not None and tz.now() > self.end_date:
            return False

        valid_statuses = [Harvest.Status.SCHEDULED]
        if not public:
            valid_statuses += [
                Harvest.Status.ADOPTED,
                Harvest.Status.PENDING,
                Harvest.Status.READY,
            ]

        return self.status in valid_statuses


@receiver(pre_save, sender=Harvest)
def harvest_changed_by(sender, instance, **kwargs):
    request = CrequestMiddleware.get_request()
    if not request:
        return
    instance.changed_by = \
        None if request.user.is_anonymous else request.user


class RequestForParticipation(models.Model):
    """Request For Participation model"""

    class Meta:
        verbose_name = _("request for participation")
        verbose_name_plural = _("requests for participation")

    class Status(models.TextChoices, Enum):
        PENDING = 'pending', _("Pending")
        ACCEPTED = 'accepted', _("Accepted")
        DECLINED = 'declined', _("Declined")
        CANCELLED = 'cancelled', _("Cancelled")
        OBSOLETE = 'obsolete', _("Obsolete")

    class Action(models.TextChoices):
        ACCEPT = 'accept', _("Accept request")
        DECLINE = 'decline', _("Decline request")

    harvest = models.ForeignKey(
        'Harvest',
        verbose_name=_("Harvest"),
        related_name='requests',
        on_delete=models.CASCADE,
    )

    person = models.ForeignKey(
        'member.Person',
        verbose_name=_("Requester"),
        related_name='requests',
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        choices=Status.choices,
        max_length=20,
        verbose_name=_("Request status"),
        default=Status.PENDING,
    )

    number_of_pickers = models.PositiveIntegerField(
        verbose_name=_("Number of pickers"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )

    comment = models.TextField(
        verbose_name=_("Comment from participant"),
        null=True,
        blank=True
    )

    notes = models.TextField(
        verbose_name=_("PickLeader notes"),
        null=True,
        blank=True
    )

    date_created = models.DateTimeField(
        verbose_name=_("Created on"),
        auto_now_add=True
    )

    date_status_updated = models.DateTimeField(
        verbose_name=_("Status updated on"),
        null=True,
        blank=True
    )

    showed_up = models.BooleanField(
        verbose_name=_("Picker(s) showed up"),
        default=None,
        null=True,
        blank=True
    )

    @staticmethod
    def get_status_choices():
        return [s[0] for s in RequestForParticipation.Status.choices]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__last_status = self.status

    def save(self, *args, **kwargs):
        if self.status != self.__last_status:
            self.__last_status = self.status
            self.date_status_updated = tz.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Request by {self.person} to participate in {self.harvest}"


class HarvestYield(models.Model):
    """Harvest Yield model"""

    class Meta:
        verbose_name = _("harvest yield")
        verbose_name_plural = _("harvest yields")

    harvest = models.ForeignKey(
        'Harvest',
        verbose_name=_("Harvest"),
        related_name='yields',
        on_delete=models.CASCADE,
    )

    tree = models.ForeignKey(
        'TreeType',
        verbose_name=_("Tree"),
        on_delete=models.CASCADE,
    )

    total_in_lb = models.FloatField(
        verbose_name=_("Weight (lb)"),
        validators=[
            MinValueValidator(0.0)
        ]
    )

    recipient = models.ForeignKey(
        'member.Actor',
        verbose_name=_("Recipient"),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "%.2f lbs of %s to %s" % \
               (self.total_in_lb, self.tree.fruit_name_en, self.recipient)


class Comment(models.Model):
    """Harvest comment model"""

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    harvest = models.ForeignKey(
        'Harvest',
        verbose_name=_("harvest"),
        related_name="comments",
        on_delete=models.CASCADE,
    )

    author = models.ForeignKey(
        'member.AuthUser',
        verbose_name=_("Author"),
        related_name="comments",
        on_delete=models.CASCADE,
    )

    content = models.CharField(
        verbose_name=_("Content"),
        max_length=500
    )

    date_created = models.DateTimeField(
        verbose_name=_("Created on"),
        auto_now_add=True
    )

    date_updated = models.DateTimeField(
        verbose_name=_("Updated on"),
        auto_now=True,
        null=True,
    )

    def __str__(self):
        return self.content


class PropertyImage(models.Model):
    """Property Image model"""

    property = models.ForeignKey(
        Property,
        related_name='images',
        on_delete=models.CASCADE,

    )
    image = models.ImageField(
        upload_to='properties_images',
    )

    def __str__(self):
        return self.property.__str__()


class HarvestImage(models.Model):
    """Harvest Image model"""

    harvest = models.ForeignKey(
        Harvest,
        related_name='images',
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to='harvests_images',
    )

    def __str__(self):
        return self.harvest.__str__()


# CACHE #

@receiver(post_save, sender=Property)
def clear_cache_property(sender, instance, **kwargs):
    cache.delete_pattern("*property*")


@receiver(post_save, sender=Harvest)
def clear_cache_harvest(sender, instance, **kwargs):
    cache.delete_pattern("*harvest*")


@receiver(post_save, sender=Equipment)
def clear_cache_equipment(sender, instance, **kwargs):
    cache.delete_pattern("*equipment*")
