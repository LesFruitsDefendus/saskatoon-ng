from rest_framework import serializers
from member.models import (
    AuthUser,
    City,
    Country,
    Neighborhood,
    Organization,
    Person,
    State,
)
from harvest.models import Harvest, Property


class NeighborhoodSerializer(serializers.ModelSerializer[Neighborhood]):
    class Meta:
        model = Neighborhood
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer[City]):
    class Meta:
        model = City
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer[State]):
    class Meta:
        model = State
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer[Country]):
    class Meta:
        model = Country
        fields = '__all__'


class PersonPropertySerializer(serializers.ModelSerializer[Property]):
    class Meta:
        model = Property
        fields = ['id', 'short_address']


class PersonHarvestSerializer(serializers.ModelSerializer[Harvest]):
    class Meta:
        model = Harvest
        fields = [
            'id',
            'pick_leader',
            'property',
            'status',
            'status_display',
            'start_date',
            'role',
            'rfp_status',
        ]

    status_display = serializers.ReadOnlyField(source='get_status_display')
    pick_leader: serializers.StringRelatedField[Harvest] = serializers.StringRelatedField(
        many=False, read_only=True
    )
    property: serializers.StringRelatedField[Harvest] = serializers.StringRelatedField(
        many=False, read_only=True
    )
    start_date = serializers.DateTimeField(source='get_local_start', format=r"%Y-%m-%d")
    # annotated fields from person.get_harvests()
    role = serializers.ReadOnlyField()
    rfp_status = serializers.ReadOnlyField()


class RequestForParticipationPersonSerializer(serializers.ModelSerializer[Person]):
    class Meta:
        model = Person
        fields = ['name', 'email', 'phone', 'accept_count', 'reject_count']

    accept_count = serializers.ReadOnlyField()
    reject_count = serializers.ReadOnlyField()


class PersonBeneficiarySerializer(serializers.ModelSerializer[Organization]):
    class Meta:
        model = Organization
        fields = ['pk', 'civil_name']


class PersonSerializer(serializers.ModelSerializer[Person]):
    class Meta:
        model = Person
        fields = [
            'actor_id',
            'roles',
            'name',
            'email',
            'phone',
            'neighborhood',
            'comments',
            'harvests',
            'organizations_as_contact',
            'properties',
        ]

    neighborhood = NeighborhoodSerializer(many=False, read_only=True)
    properties = PersonPropertySerializer(many=True, read_only=True)

    harvests = PersonHarvestSerializer(source='get_harvests', many=True, read_only=True)

    organizations_as_contact = PersonBeneficiarySerializer(
        source='get_organizations_as_contact', many=True, read_only=True
    )
    roles = serializers.SerializerMethodField()

    def get_roles(self, person):
        if hasattr(person, 'auth_user'):
            return [str(role) for role in person.auth_user.roles]
        return ""


class ContactPersonSerializer(PersonSerializer):
    class Meta:
        model = Person
        fields = ['actor_id', 'roles', 'name', 'email', 'phone']


class PersonOwnerSerializer(serializers.ModelSerializer[Person]):
    class Meta:
        model = Person
        fields = [
            'pk',
            'name',
            'email',
            'phone',
            'language',
            'comments',
            'neighborhood',
            'city',
            'state',
            'country',
        ]

    comments = serializers.SerializerMethodField()

    def get_comments(self, person):
        return person.comments


class OrganizationOwnerSerializer(serializers.ModelSerializer[Organization]):
    class Meta:
        model = Organization
        fields = [
            'pk',
            'name',
            'email',
            'phone',
            'neighborhood',
            'city',
            'state',
            'country',
            'comments',
        ]

    comments = serializers.SerializerMethodField()

    def get_comments(self, org):
        return org.contact_person.comments


class PickerSerializer(serializers.ModelSerializer[Person]):
    class Meta:
        model = Person
        fields = ['pk', 'name']


class PickLeaderSerializer(serializers.ModelSerializer[AuthUser]):
    class Meta:
        model = AuthUser
        fields = ['id', 'name', 'email']


class CommunitySerializer(serializers.ModelSerializer[AuthUser]):
    class Meta:
        model = AuthUser
        fields = '__all__'

    person = PersonSerializer(many=False, read_only=True)
    roles = serializers.ReadOnlyField()
    role_codes = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(format="%Y-%m-%d")

    def get_role_codes(self, instance):
        return [g.name for g in instance.role_groups]
