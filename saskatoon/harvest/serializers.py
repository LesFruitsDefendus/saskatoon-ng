from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from member.models import Actor, Organization
from member.serializers import (
    NeighborhoodSerializer,
    CitySerializer,
    CountrySerializer,
    StateSerializer,
    PersonOwnerSerializer,
    PersonRFPSerializer,
    PersonSerializer,
    PickLeaderSerializer,
    PickerSerializer,
)
from harvest.models import (
    Comment,
    Equipment,
    EquipmentType,
    Harvest,
    HarvestYield,
    Property,
    RequestForParticipation as RFP,
    TreeType,
)
from harvest.utils import similar_properties


class TreeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeType
        fields = '__all__'


class RequestForParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RFP
        fields = '__all__'

    person = PersonRFPSerializer(many=False)
    date_created = serializers.DateTimeField(format=r"%Y-%m-%d")
    time_created = serializers.DateTimeField(source='date_created', format=r"%I:%H %p")
    date_status_updated = serializers.DateTimeField(format=r"%Y-%m-%d")


class OrganizationOwnerSerializer(PersonOwnerSerializer):
    class Meta(PersonOwnerSerializer.Meta):
        model = Organization

    def get_comments(self, obj):
        return _("Owner is an Organization")


class OwnerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['is_person', 'is_organization']


class PropertyHarvestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvest
        fields = [
            'id',
            'status',
            'status_display',
            'start_date',
            'start_time',
            'end_date',
            'pick_leader',
            'trees',
        ]

    status_display = serializers.ReadOnlyField(source='get_status_display')
    pick_leader = serializers.SerializerMethodField()
    trees = TreeTypeSerializer(many=True, read_only=True)
    start_date = serializers.DateTimeField(
        source='get_local_start',
        format=r"%Y-%m-%d"
    )
    start_time = serializers.DateTimeField(
        source='get_local_start',
        format=r"%-I:%M %p"
    )
    end_date = serializers.DateTimeField(
        source='get_local_end',
        format=r"%Y-%m-%d"
    )

    def get_pick_leader(self, harvest):
        if harvest.pick_leader:
            return PersonSerializer(harvest.pick_leader.person).data
        return None


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

    neighborhood = NeighborhoodSerializer(many=False, read_only=True)
    city = CitySerializer(many=False, read_only=True)
    state = StateSerializer(many=False, read_only=True)
    country = CountrySerializer(many=False, read_only=True)
    title = serializers.ReadOnlyField(source="__str__")
    harvests = PropertyHarvestSerializer(many=True, read_only=True)
    last_succeeded_harvest_date = serializers.ReadOnlyField()
    address = serializers.ReadOnlyField(source="short_address")
    trees = TreeTypeSerializer(many=True, read_only=True)
    owner = serializers.SerializerMethodField()
    pending_contact_name = serializers.ReadOnlyField()
    owner_type = serializers.SerializerMethodField()
    similar_properties = serializers.SerializerMethodField()
    needs_orphan = serializers.ReadOnlyField()

    def get_owner(self, obj):
        if obj.owner:
            if obj.owner.is_person:
                return PersonOwnerSerializer(obj.owner.person).data
            elif obj.owner.is_organization:
                return OrganizationOwnerSerializer(obj.owner.organization).data
        return None

    def get_owner_type(self, obj):
        return OwnerTypeSerializer(obj.owner).data

    def get_similar_properties(self, obj):
        return similar_properties(obj)


class PropertyListHarvestSerializer(PropertyHarvestSerializer):
    start_date = serializers.DateTimeField(
        source='get_local_start',
        format="%Y-%m-%d"
    )
    pick_leader = serializers.StringRelatedField(many=False)


class PropertyTreeTypeSerializer(TreeTypeSerializer):
    class Meta(TreeTypeSerializer.Meta):
        fields = [  # type: ignore
            'id',
            'name_en',
            'name_fr',
            'fruit_name_en',
            'fruit_name_fr',
            'fruit_icon',
        ]


class PropertyListSerializer(PropertySerializer):
    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'neighborhood',
            'trees',
            'ladder_available',
            'last_succeeded_harvest_date',
            'is_active',
            'authorized',
            'pending',
            'harvests'
        ]

    neighborhood = serializers.StringRelatedField(many=False)
    trees = PropertyTreeTypeSerializer(many=True, read_only=True)
    harvests = PropertyListHarvestSerializer(many=True, read_only=True)


class PropertyEquipmentSerializer(PropertyListSerializer):
    class Meta(PropertyListSerializer.Meta):
        fields = [
            'id',
            'title',
            'neighborhood',
            'owner'
        ]


class HarvestYieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestYield
        fields = '__all__'

    tree = TreeTypeSerializer(many=False, read_only=True)
    recipient = serializers.StringRelatedField(many=False)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    author = PickLeaderSerializer(many=False, read_only=True)
    date_created = serializers.DateTimeField(format=r'%c')
    date_updated = serializers.DateTimeField(format=r'%c')


class HarvestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvest
        fields = '__all__'

    total_distribution = serializers.ReadOnlyField(
        source='get_total_distribution'
    )
    volunteers_count = serializers.SerializerMethodField()
    is_open_to_requests = serializers.SerializerMethodField()
    is_open_to_public_requests = serializers.SerializerMethodField()
    start_date = serializers.DateTimeField(
        source='get_local_start',
        format=r"%a. %b. %-d, %Y"
    )
    start_time = serializers.DateTimeField(
        source='get_local_start',
        format=r"%-I:%M %p"
    )
    end_time = serializers.DateTimeField(
        source='get_local_end',
        format=r"%-I:%M %p"
    )
    status = serializers.StringRelatedField(many=False)
    status_display = serializers.ReadOnlyField(source='get_status_display')
    pick_leader = PickLeaderSerializer(many=False, read_only=True)
    trees = TreeTypeSerializer(many=True, read_only=True)
    property = PropertySerializer(many=False, read_only=True)
    requests = RequestForParticipationSerializer(many=True, read_only=True)
    yields = HarvestYieldSerializer(many=True, read_only=True)
    comment = CommentSerializer(many=True, read_only=True)
    pickers = serializers.SerializerMethodField()
    organizations = serializers.SerializerMethodField()
    maturity_range = serializers.SerializerMethodField()

    def get_volunteers_count(self, obj):
        return obj.get_volunteers_count(status=RFP.Status.ACCEPTED)

    def get_is_open_to_requests(self, obj):
        return obj.is_open_to_requests(False)

    def get_is_open_to_public_requests(self, obj):
        return obj.is_open_to_requests(True)

    def get_pickers(self, obj):
        # used for the Fruit Distribution recipient list (includes pick_leader)
        rfps = obj.requests.filter(status=RFP.Status.ACCEPTED).select_related('person')
        pickers = [obj.pick_leader.person] + [rfp.person for rfp in rfps]
        return PickerSerializer(pickers, many=True).data

    def get_organizations(self, obj):
        organizations = Organization.objects.filter(is_beneficiary=True)
        return OrganizationSerializer(organizations, many=True).data

    def get_maturity_range(self, obj):
        if obj.trees.count() == 1:
            return obj.trees.first().maturity_range
        return "{} - {}".format(
            obj.start_date.strftime("%b. %-d"),
            obj.end_date.strftime("%b. %-d, %Y"),
        )


class HarvestBeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['actor_id', 'civil_name']


class HarvestDetailPropertySerializer(PropertySerializer):
    class Meta(PropertySerializer.Meta):
        fields = [
            'id',
            'title',
            'address',
            'owner',
            'neighborhood'
        ]  # type: ignore

    neighborhood = serializers.StringRelatedField(many=False)


class HarvestDetailSerializer(HarvestSerializer):
    class Meta:
        model = Harvest
        exclude = [
            'owner_present',
            'owner_help',
            'owner_fruit',
            'publication_date',
            'equipment_reserved',
            'date_created',
            'changed_by'
        ]

    trees = PropertyTreeTypeSerializer(many=True, read_only=True)
    property = HarvestDetailPropertySerializer(many=False, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    about = serializers.SerializerMethodField()
    status_choices = serializers.SerializerMethodField()

    def get_about(self, obj):
        return obj.about.html

    def get_status_choices(self, _obj):
        return Harvest.get_status_choices()


class HarvestListPropertySerializer(PropertySerializer):
    class Meta(PropertySerializer.Meta):
        fields = [
            'id',
            'title',
            'ladder_available',
            'neighborhood'
        ]  # type: ignore

    neighborhood = serializers.StringRelatedField(many=False)


class HarvestListSerializer(HarvestSerializer):
    class Meta:
        model = Harvest
        fields = [
            'id',
            'start_date',
            'start_time',
            'end_time',
            'status',
            'status_display',
            'pick_leader',
            'trees',
            'property',
            'volunteers'
        ]

    status_display = serializers.ReadOnlyField(source='get_status_display')
    property = HarvestListPropertySerializer(many=False, read_only=True)
    trees = PropertyTreeTypeSerializer(many=True, read_only=True)
    volunteers = serializers.SerializerMethodField()

    def get_volunteers(self, harvest):
        return dict([(s, harvest.get_volunteers_count(s)) for s in RFP.get_status_choices()])


class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = ['name', 'name_fr', 'name_en']

    name = serializers.SerializerMethodField()

    def get_name(self, type):
        return type.name_fr


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

    property = PropertyEquipmentSerializer(many=False, read_only=True)
    type = EquipmentTypeSerializer(many=False, read_only=True)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'actor_id',
            'civil_name',
            'contact_person',
            'phone',
            'short_address',
            'address',
            'neighborhood',
            'description',
            'is_beneficiary',
            'beneficiary_description',
            'is_equipment_point',
            'equipment_description',
            'equipment',
            'inventory'
        ]

    contact_person = PersonSerializer(many=False, read_only=True)
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    inventory = serializers.SerializerMethodField()

    def get_inventory(self, org):
        return dict([
            (lang, "&;".join([e.inventory(lang) for e in org.equipment.all()]))
            for lang in ['fr', 'en']
        ])
