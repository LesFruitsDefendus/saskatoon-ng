import json
from django.core.serializers import serialize
from rest_framework import serializers
from member.models import (Actor, Neighborhood, AuthUser, Person, Organization,
                           City, State, Country, Language)
from harvest.models import (Harvest, Property, Equipment, EquipmentType,
                            RequestForParticipation, TreeType)


class RequestForParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestForParticipation
        fields = '__all__'


class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)

    class Meta:
        model = Person
        fields = ['actor_id', 'name', 'email', 'phone', 'neighborhood',
                  'harvests_as_pickleader', 'harvests_as_volunteer_accepted',
                  'harvests_as_volunteer_pending', 'harvests_as_volunteer_missed',
                  'harvests_as_owner', 'properties']


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
        fields = ['pk', 'name', 'email', 'phone', 'language',
                  'neighborhood', 'city', 'state', 'country']

    language = serializers.SerializerMethodField()

    def get_language(self, obj):
        return obj.language.name if obj.language else None


class OrganizationOwnerSerializer(PersonOwnerSerializer):
    class Meta(PersonOwnerSerializer.Meta):
        model = Organization


class OwnerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['is_person', 'is_organization']


# Property serializer
class PropertySerializer(serializers.ModelSerializer):
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)
    city = CitySerializer(many=False, read_only=True)
    state = StateSerializer(many=False, read_only=True)
    country = CountrySerializer(many=False, read_only=True)
    title = serializers.ReadOnlyField(source="__str__")
    harvests = serializers.ReadOnlyField(source="get_harvests")
    last_succeeded_harvest = serializers.ReadOnlyField(source="get_last_succeeded_harvest")
    address = serializers.ReadOnlyField(source="short_address")
    trees = TreeTypeSerializer(many=True, read_only=True)
    owner = serializers.SerializerMethodField()
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

# Harvest serializer
class HarvestSerializer(serializers.ModelSerializer):

    # three different ways of getting a multimodel serializer:
    # 1) calling a model method
    pickers = serializers.ReadOnlyField(source='get_pickers')
    total_distribution = serializers.ReadOnlyField(source='get_total_distribution')
    # status_l10n = serializers.ReadOnlyField(source='get_status_l10n')
    start_date = serializers.DateTimeField(source='get_local_start', format="%Y-%m-%d")
    start_time = serializers.DateTimeField(source='get_local_start', format="%H:%M")
    end_time = serializers.DateTimeField(source='get_local_end', format="%H:%M")
    # # 2) get string rather than id from a pk
    status = serializers.StringRelatedField(many=False)
    pick_leader = serializers.StringRelatedField(many=False)
    # 3) get the full instance from another serializer class
    trees = TreeTypeSerializer(many=True, read_only=True)
    property = PropertySerializer(many=False, read_only=True)

    class Meta:
        model = Harvest
        fields = '__all__'

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
