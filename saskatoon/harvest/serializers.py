from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from member.models import (Actor, Neighborhood, AuthUser, Person, Organization,
                           City, State, Country)
from harvest.models import (Harvest, Property, Equipment, EquipmentType,
                            RequestForParticipation, TreeType)


class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = '__all__'


class PersonPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'short_address']


class PersonHarvestSerializer(serializers.ModelSerializer):
    pick_leader = serializers.StringRelatedField(many=False, read_only=True)
    property = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Harvest
        fields = ['id', 'pick_leader', 'property']


class PersonSerializer(serializers.ModelSerializer):
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)
    properties = PersonPropertySerializer(many=True, read_only=True)
    harvests_as_pickleader = PersonHarvestSerializer(many=True, read_only=True)
    harvests_as_volunteer_accepted = PersonHarvestSerializer(many=True, read_only=True)
    harvests_as_volunteer_pending = PersonHarvestSerializer(many=True, read_only=True)
    harvests_as_volunteer_missed = PersonHarvestSerializer(many=True, read_only=True)
    harvests_as_owner = PersonHarvestSerializer(many=True, read_only=True)
    organizations_as_contact = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Person
        fields = ['actor_id', 'name', 'email', 'phone', 'neighborhood',
                  'harvests_as_pickleader', 'harvests_as_volunteer_accepted',
                  'harvests_as_volunteer_pending', 'harvests_as_volunteer_missed',
                  'harvests_as_owner', 'organizations_as_contact', 'properties', 'comments']


class RequestForParticipationSerializer(serializers.ModelSerializer):
    picker = PersonSerializer(many=False)
    creation_date = serializers.DateTimeField( format=r"%Y-%m-%d")
    acceptation_date = serializers.DateTimeField( format=r"%Y-%m-%d")

    class Meta:
        model = RequestForParticipation
        fields = '__all__'


class BeneficiarySerializer(serializers.ModelSerializer):
    contact_person = PersonSerializer(many=False, read_only=True)
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)

    class Meta:
        model = Organization
        fields = ['actor_id', 'civil_name', 'phone', 'short_address', 'description',
                  'is_beneficiary', 'contact_person', 'neighborhood']


class ActorSerializer(serializers.ModelSerializer):
    person = PersonSerializer(source='get_person', many=False, read_only=True)
    organization = BeneficiarySerializer(source='get_organization', many=False, read_only=True)
    class Meta:
        model = Actor
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class TreeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeType
        fields = '__all__'


class PersonOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['pk', 'name', 'email', 'phone', 'language', 'comments',
                  'neighborhood', 'city', 'state', 'country']

    language = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    def get_language(self, obj):
        return obj.language.name if obj.language else None

    def get_comments(self, obj):
        return obj.person.comments


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
        fields = ['id', 'status', 'start_date', 'pick_leader']

    pick_leader = serializers.SerializerMethodField()

    def get_pick_leader(self, harvest):
        if harvest.pick_leader:
            return PersonSerializer(harvest.pick_leader.person).data
        return None


# Property serializer
class PropertySerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Property
        fields = '__all__'

    def get_owner(self, obj):
        if obj.owner:
            if obj.owner.is_person:
                return PersonOwnerSerializer(obj.owner.person).data
            elif obj.owner.is_organization:
                return OrganizationOwnerSerializer(obj.owner.organization).data
        return None

    def get_owner_type(self, obj):
        return OwnerTypeSerializer(obj.owner).data


class PropertyListHarvestSerializer(PropertyHarvestSerializer):
    start_date = serializers.DateTimeField(source='get_local_start', format="%Y-%m-%d")
    pick_leader = serializers.StringRelatedField(many=False)


class PropertyTreeTypeSerializer(TreeTypeSerializer):
    class Meta(TreeTypeSerializer.Meta):
        fields = ['name', 'fruit_name']


class PropertyListSerializer(PropertySerializer):
    neighborhood = serializers.StringRelatedField(many=False)
    trees = PropertyTreeTypeSerializer(many=True, read_only=True)
    harvests = PropertyListHarvestSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'neighborhood',
            'trees',
            'last_succeeded_harvest_date',
            'is_active',
            'authorized',
            'pending',
            'harvests'
        ]


# EquipmentType serializer
class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = '__all__'

# Equipment serializer
class EquipmentSerializer(serializers.ModelSerializer):
    property = PropertySerializer(many=False, read_only=True)
    type = EquipmentTypeSerializer(many=False, read_only=True)
    owner = ActorSerializer(many=False, read_only=True)
    class Meta:
        model = Equipment
        fields = '__all__'


class HarvestYieldSerializer(serializers.ModelSerializer):
    tree = TreeTypeSerializer(many=False, read_only=True)
    recipient = serializers.StringRelatedField(many=False)

    class Meta:
        model = HarvestYield
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format=r'%c')
    author = serializers.StringRelatedField(many=False)

    class Meta:
        model = Comment
        fields = '__all__'


# Harvest serializer
class HarvestSerializer(serializers.ModelSerializer):

    # three different ways of getting a multimodel serializer:
    # 1) calling a model method
    pickers = serializers.ReadOnlyField(source='get_pickers')
    total_distribution = serializers.ReadOnlyField(source='get_total_distribution')
    # status_l10n = serializers.ReadOnlyField(source='get_status_l10n')
    start_date = serializers.DateTimeField(source='get_local_start', format=r"%a. %b. %-d, %Y")
    start_time = serializers.DateTimeField(source='get_local_start', format=r"%-I:%M %p")
    end_time = serializers.DateTimeField(source='get_local_end', format=r"%-I:%M %p")
    # # 2) get string rather than id from a pk
    status = serializers.StringRelatedField(many=False)
    pick_leader = serializers.StringRelatedField(many=False)
    # 3) get the full instance from another serializer class
    trees = TreeTypeSerializer(many=True, read_only=True)
    property = PropertySerializer(many=False, read_only=True)
    requests = RequestForParticipationSerializer(many=True, read_only=True)
    harvestyield_set = HarvestYieldSerializer(many=True, read_only=True)
    comment = CommentSerializer(many=True, read_only=True)
    organizations = serializers.SerializerMethodField()

    class Meta:
        model = Harvest
        fields = '__all__'

    def get_organizations(self, obj):
        organizations = Organization.objects.filter(
            is_beneficiary=True)
        return BeneficiarySerializer(organizations, many=True).data


class HarvestTreeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeType
        fields = ['id', 'name', 'fruit_name']


class HarvestListSerializer(HarvestSerializer):
    property = serializers.StringRelatedField(many=False)
    neighborhood = serializers.ReadOnlyField(source='get_neighborhood')
    trees = HarvestTreeTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Harvest
        fields = ['id',
                  'start_date',
                  'start_time',
                  'end_time',
                  'status',
                  'pick_leader',
                  'trees',
                  'property',
                  'neighborhood']


# Community serializer
class CommunitySerializer(serializers.ModelSerializer):
    person = PersonSerializer(many=False, read_only=True)
    roles = serializers.ReadOnlyField()
    role_codes = serializers.SerializerMethodField()
    class Meta:
        model = AuthUser
        fields = '__all__'

    def get_role_codes(self, instance):
        return [g.name for g in instance.role_groups]
