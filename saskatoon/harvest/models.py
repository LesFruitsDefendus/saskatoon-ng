# coding: utf-8

from harvest import signals
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import datetime
from djgeojson.fields import PointField
from phone_field import PhoneField
from django.db.models.query_utils import Q


HARVESTS_STATUS_CHOICES = (
    (
        "To-be-confirmed",
        _("To be confirmed"),
    ),
    (
        "Orphan",
        _("Orphan"),
    ),
    (
        "Adopted",
        _("Adopted"),
    ),
    (
        "Date-scheduled",
        _("Date scheduled"),
    ),
    (
        "Ready",
        _("Ready"),
    ),
    (
        "Succeeded",
        _("Succeeded"),
    ),
    (
        "Cancelled",
        _("Cancelled"),
    )
)


class TreeType(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=20,
        default=''
    )

    image = models.ImageField(
        upload_to='fruits_images',
        verbose_name=_("Fruit image"),
        null=True
    )

    fruit_name = models.CharField(
        verbose_name=_("Fruit name"),
        max_length=20
    )

    season_start = models.DateField(
        verbose_name=_("Season start date"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("tree type")
        verbose_name_plural = _("tree types")
        ordering = ["name"]

    def __str__(self):
        return self.name


class EquipmentType(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=50
    )

    class Meta:
        verbose_name = _("equipment type")
        verbose_name_plural = _("equipment types")

    def __str__(self):
        return self.name


class Property(models.Model):
    """
    Property where you find one or more trees for harvesting.
    """
    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        help_text=_("This property exists and may be able to host a pick"),
        default=True
    )

    authorized = models.BooleanField(
        verbose_name=_("Authorized for this season"),
        help_text=_("Harvest in this property has been authorized for the current season by its owner"),
        null=True,
        default=None
    )

    pending = models.BooleanField(
        verbose_name=_("Pending"),
        help_text=_("This property was created through a public form and needs to be validated by an administrator"),
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

    owner = models.ForeignKey(
        'member.Actor',
        null=True,
        blank=True,
        verbose_name=_("Owner"),
        on_delete=models.CASCADE,
    )

    # FIXME: add help_text in forms.py
    trees = models.ManyToManyField(
        'TreeType',
        verbose_name=_("Fruit tree/vine type(s)"),
        help_text=_(
            'Select multiple fruit types if applicable. Unknown fruit type or colour can be mentioned in the additional comments at the bottom.'),
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
        verbose_name=_("A ladder is available in the property and can be used for nearby picks"),
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
        help_text=_("Aproximative location to be used in public communications (not the actual address)"),
        max_length=50,
        null=True,
        blank=True
    )

    neighborhood = models.ForeignKey(
        'member.Neighborhood',
        verbose_name=_("Neighborhood"),
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

    class Meta:
        verbose_name = _("property")
        verbose_name_plural = _("properties")

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
        """Returns the start_date of the last successful Harvest in this Property"""
        last_harvest = self.harvests.filter(status="Succeeded").order_by('start_date').last()
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

    def __str__(self):
        number = self.street_number if self.street_number else ""
        return u"%s %s %s %s" % (self.owner_name, _("at"), number, self.street)

    @property
    def pending_contact_name(self):
        if self.pending_contact_first_name and self.pending_contact_family_name:
            return " ".join([self.pending_contact_first_name, self.pending_contact_family_name])
        elif self.pending_contact_first_name:
            return self.pending_contact_first_name
        elif self.pending_contact_family_name:
            return self.pending_contact_family_name
        else:
            return ""

class Harvest(models.Model):

    PUBLISHABLE_STATUSES = ['Ready', 'Date-scheduled', 'Succeeded']

    status = models.CharField(
        choices=HARVESTS_STATUS_CHOICES,
        max_length=100,
        null=True,
        verbose_name=_("Harvest status")
    )

    property = models.ForeignKey(
        'Property',
        null=True,
        verbose_name=_("Property"),
        related_name='harvests',
        on_delete=models.CASCADE,
    )

    trees = models.ManyToManyField(
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

    equipment_reserved = models.ManyToManyField(
        'Equipment',
        verbose_name=_("Reserve equipment"),
        blank=True
    )

    creation_date = models.DateTimeField(
        verbose_name=_("Creation date"),
        auto_now=False,
        auto_now_add=True
    )

    nb_required_pickers = models.PositiveIntegerField(
        verbose_name=_("Number of required pickers"),
        default=3
    )

    about = models.TextField(
        verbose_name=_("Public announcement"),
        max_length=1000,
        help_text=_("If any help is needed from volunteer pickers, "
                    "please describe them here."),
        null=True,
        blank=True
    )

    changed_by = models.ForeignKey(
        'member.AuthUser',
        related_name='harvest_edited',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    def get_status_l10n(self):
        status_list = list(HARVESTS_STATUS_CHOICES)
        for s in status_list:
            if s[0] in self.status:
                return s[1]

    def get_total_distribution(self):
        total = 0
        yields = HarvestYield.objects.filter(harvest=self)
        for y in yields:
            total += y.total_in_lb
        return total

    def get_local_start(self):
        tz = timezone.get_current_timezone()
        return self.start_date.astimezone(tz) if self.start_date else self.start_date

    def get_local_end(self):
        tz = timezone.get_current_timezone()
        return self.end_date.astimezone(tz) if self.end_date else self.end_date

    class Meta:
        verbose_name = _("harvest")
        verbose_name_plural = _("harvests")
        ordering = ['-start_date']

    def __str__(self):
        if self.start_date:
            return (_("Harvest on {} for {}")).format(
                self.get_local_start().strftime("%d/%m/%Y %H:%M"),
                self.property
            )
        else:
            return (_("Harvest for {}")).format(
                self.property
            )

    def get_pickers(self):
        requests = RequestForParticipation.objects.filter(harvest=self).filter(is_accepted=True)
        return requests.values('picker_id', 'picker__first_name', 'picker__family_name')

    def get_unselected_pickers(self):
        # Get pickers who volunteered but have been rejected or are pending approval
        requests = self.requests.exclude(Q(is_accepted=True) | Q(is_cancelled=True))
        return [r.picker for r in requests]

    def get_days_before_harvest(self):
        diff = datetime.datetime.now() - self.start_date
        return diff.days

    def get_neighborhood(self):
        return self.property.neighborhood

    def get_fruits(self):
        return [t.fruit_name for t in self.trees.all()]

    def get_public_title(self):
        title = ", ".join(self.get_fruits())
        if self.property.neighborhood.name != "Other":
           title += f" @ {self.property.neighborhood.name}"
        return title

    # @property  # WARNING: decorator conflicts with property field :/
    def is_urgent(self):
        NUM_DAYS_URGENT_ORPHAN = 14
        NUM_DAYS_URGENT_NOT_READY = 3
        if not self.start_date:
            return False
        days = self.get_days_before_harvest()
        if self.status == 'Orphan' and days < NUM_DAYS_URGENT_ORPHAN:
            return True
        elif self.status == 'Date-scheduled' and days < NUM_DAYS_URGENT_NOT_READY:
            return True
        return False

    def is_happening(self):
        if not self.start_date:
            return False
        is_today = self.get_days_before_harvest() == 0
        return (self.status == 'Ready' and is_today)

    def is_publishable(self):
        if self.status not in self.PUBLISHABLE_STATUSES:
            return False
        if not self.publication_date:
            return True
        return (timezone.now() > self.publication_date)

    def is_open_to_requests(self):
        if self.status != 'Date-scheduled':
            return False
        return timezone.now() <= self.end_date


class RequestForParticipation(models.Model):
    picker = models.ForeignKey(
        'member.Person',
        verbose_name=_("Requester"),
        on_delete=models.CASCADE,
    )

    number_of_people = models.PositiveIntegerField(
        verbose_name=_("How many people are you?"),
        default=1,
        validators=[MinValueValidator(1)]
    )

    comment = models.TextField(
        verbose_name=_("Comment"),
        null=True,
        blank=True
    )

    notes_from_pickleader = models.TextField(
        verbose_name=_("Notes from the pick leader."),
        null=True,
        blank=True
    )

    harvest = models.ForeignKey(
        'Harvest',
        verbose_name=_("Harvest"),
        related_name="requests",
        on_delete=models.CASCADE,
    )

    creation_date = models.DateTimeField(
        verbose_name=_("Created on"),
        default=timezone.now
    )

    acceptation_date = models.DateTimeField(
        verbose_name=_("Accepted on"),
        null=True,
        blank=True
    )

    is_accepted = models.BooleanField(
        verbose_name=_("Accepted"),
        default=None,
        null=True,
        blank=True
    )

    showed_up = models.BooleanField(
        verbose_name=_("Showed up"),
        default=None,
        null=True,
        blank=True
    )

    is_cancelled = models.BooleanField(
        verbose_name=_("Canceled"),
        default=False
    )

    class Meta:
        verbose_name = _("request for participation")
        verbose_name_plural = _("requests for participation")

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_date = timezone.now()
        super(RequestForParticipation, self).save(*args, **kwargs)

    def __str__(self):
        return "Request by %s to participate to %s" % \
               (self.picker, self.harvest)


class HarvestYield(models.Model):
    harvest = models.ForeignKey(
        'Harvest',
        verbose_name=_("Harvest"),
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

    class Meta:
        verbose_name = _("harvest yield")
        verbose_name_plural = _("harvest yields")

    def __str__(self):
        return "%.2f lbs of %s to %s" % \
               (self.total_in_lb, self.tree.fruit_name, self.recipient)


class Equipment(models.Model):
    type = models.ForeignKey(
        'EquipmentType',
        verbose_name=_("Type"),
        on_delete=models.CASCADE,
    )

    description = models.CharField(
        verbose_name=_("Description"),
        max_length=50
    )

    owner = models.ForeignKey(
        'member.Actor',
        verbose_name=_("Owner"),
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

    shared = models.BooleanField(
        verbose_name=_("Shared"),
        help_text=_("Can be used in harvests outside of property"),
        default=False
    )

    class Meta:
        verbose_name = _("equipment")
        verbose_name_plural = _("equipment")

    def __str__(self):
        return "%s (%s)" % (self.description, self.type)


class Comment(models.Model):
    content = models.CharField(
        verbose_name=_("Content"),
        max_length=500
    )

    created_date = models.DateTimeField(
        verbose_name=_("Created date"),
        auto_now_add=True
    )

    author = models.ForeignKey(
        'member.AuthUser',
        verbose_name=_("Author"),
        related_name="Comment",
        on_delete=models.CASCADE,
    )

    harvest = models.ForeignKey(
        'Harvest',
        verbose_name=_("harvest"),
        related_name="comment",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")

    def __str__(self):
        return self.content


class PropertyImage(models.Model):
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


####### SIGNALS ##################

# Property signals
models.signals.pre_save.connect(
    receiver=signals.changed_by,
    sender=Property
)

models.signals.pre_save.connect(
    receiver=signals.notify_pending_status_update,
    sender=Property
)

models.signals.post_save.connect(
    receiver=signals.clear_cache_property,
    sender=Property
)

# Send email on new comments
models.signals.post_save.connect(
    signals.comment_send_mail,
    sender=Comment
)

# Harvest signals
models.signals.pre_save.connect(
    signals.changed_by,
    sender=Harvest
)

models.signals.pre_save.connect(
    receiver=signals.notify_unselected_pickers,
    sender=Harvest
)

models.signals.post_save.connect(
    receiver=signals.clear_cache_harvest,
    sender=Harvest
)

# RFP signal
models.signals.post_save.connect(
    signals.rfp_send_mail,
    sender=RequestForParticipation
)

# Equipment signal
models.signals.post_save.connect(
    receiver=signals.clear_cache_equipment,
    sender=Equipment
)
