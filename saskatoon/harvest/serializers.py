from rest_framework import serializers
from harvest.models import Harvest, Property, Equipment, EquipmentType, RequestForParticipation, TreeType
from member.models import Actor, Neighborhood, AuthUser, Person, Organization, City, State, Country
from django.core.serializers import serialize
import json

# RequestForParticipation serializer
class RequestForParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestForParticipation
        fields = '__all__'

# Neighborhood serializer
class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = '__all__'

# Person serializer
class PersonSerializer(serializers.ModelSerializer):
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)

    class Meta:
        model = Person
        fields = ['actor_id', 'name', 'email', 'phone', 'neighborhood',
                  'harvests_as_pickleader', 'harvests_as_volunteer_accepted',
                  'harvests_as_volunteer_pending', 'harvests_as_volunteer_missed',
                  'harvests_as_owner', 'properties']

# Beneficiary serializer
class BeneficiarySerializer(serializers.ModelSerializer):
    contact_person = PersonSerializer(many=False, read_only=True)
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)

    class Meta:
        model = Organization
        fields = ['actor_id', 'civil_name', 'phone', 'short_address', 'description',
                  'is_beneficiary', 'contact_person', 'neighborhood']

# Actor serializer
class ActorSerializer(serializers.ModelSerializer):
    person = PersonSerializer(source='get_person', many=False, read_only=True)
    organization = BeneficiarySerializer(source='get_organization', many=False, read_only=True)
    class Meta:
        model = Actor
        fields = '__all__'

# City serializer
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

# State serializer
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

# Country serializer
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class TreeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeType
        fields = '__all__'

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

    class Meta:
        model = Property
        fields = '__all__'

    def get_owner(self, obj):
        # This will check if property owner (which is an Actor)
        # is a Person or an Organization and will serialize the result.
        # A solution could also be something like this
        # https://stackoverflow.com/questions/33137165/django-rest-framework-abstract-class-serializer/33137535#33137535

        if isinstance(obj.owner, Actor):
            entity = Person.objects.filter(actor_id=obj.owner.actor_id)
            if not entity:
                entity = Organization.objects.filter(actor_id=obj.owner.actor_id)
            if not entity:
                return None

            entity_serialized = serialize('json', entity)

            j = json.loads(entity_serialized[1:-1])
            j['fields']['neighborhood'] = str(entity[0].neighborhood)
            j['fields']['name'] = str(entity[0].name())
            j['fields']['city'] = str(entity[0].city)
            j['fields']['state'] = str(entity[0].state)
            j['fields']['country'] = str(entity[0].country)
            j['fields']['email'] = str(entity[0].email())
            if isinstance(entity[0], Person):
                j['fields']['language'] = str(entity[0].language)

            return j
        else:
            return None

# Property info serializer
# This is needed for HarvestSerializer
class PropertyInfoSerializer(serializers.ModelSerializer):
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)
    title = serializers.ReadOnlyField(source="__str__")
    address = serializers.ReadOnlyField(source="short_address")
    class Meta:
        model = Property
        fields = '__all__'

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
    property = PropertyInfoSerializer(many=False, read_only=True)

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
