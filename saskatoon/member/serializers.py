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


class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
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


class PersonPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'short_address']


class PersonHarvestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvest
        fields = ['id', 'pick_leader', 'property', 'status']

    pick_leader = serializers.StringRelatedField(many=False, read_only=True)
    property = serializers.StringRelatedField(many=False, read_only=True)


class PersonBeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['pk', 'civil_name']


class PersonSerializer(serializers.ModelSerializer):
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
            'harvests_as_owner',
            'harvests_as_pickleader',
            'harvests_as_volunteer_accepted',
            'harvests_as_volunteer_cancelled',
            'harvests_as_volunteer_pending',
            'harvests_as_volunteer_rejected',
            'harvests_as_volunteer_succeeded',
            'organizations_as_contact',
            'properties',
        ]

    neighborhood = NeighborhoodSerializer(many=False, read_only=True)
    properties = PersonPropertySerializer(many=True, read_only=True)
    harvests_as_pickleader = PersonHarvestSerializer(many=True, read_only=True)
    harvests_as_volunteer_accepted = PersonHarvestSerializer(many=True, read_only=True)
    harvests_as_volunteer_pending = PersonHarvestSerializer(many=True, read_only=True)
    harvests_as_owner = PersonHarvestSerializer(many=True, read_only=True)
    organizations_as_contact = PersonBeneficiarySerializer(many=True, read_only=True)
    roles = serializers.SerializerMethodField()

    def get_roles(self, person):
        if hasattr(person, 'auth_user'):
            return [str(role) for role in person.auth_user.roles]
        return ""


class PersonRFPSerializer(PersonSerializer):
    class Meta(PersonSerializer.Meta):
        fields = ['name', 'email', 'phone']


class PersonOwnerSerializer(serializers.ModelSerializer):
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
            'country'
        ]

    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        return obj.person.comments


class PickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['pk', 'name']


class PickLeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'name']


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = '__all__'

    person = PersonSerializer(many=False, read_only=True)
    roles = serializers.ReadOnlyField()
    role_codes = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(
        format="%Y-%m-%d"
    )

    def get_role_codes(self, instance):
        return [g.name for g in instance.role_groups]
