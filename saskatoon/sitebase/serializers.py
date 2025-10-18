from django.urls import reverse_lazy
from rest_framework import serializers

from harvest.models import Harvest, Comment, Property, RequestForParticipation
from member.models import AuthUser, Person
from saskatoon.settings import DOMAIN_NAME


def add_key_prefix(serializer, obj, key):
    d = super(type(serializer), serializer).to_representation(obj)
    return {f"{key}_{k}": v for k, v in d.items()}


class EmailRecipientSerializer(serializers.ModelSerializer[Person]):
    class Meta:
        model = Person
        fields = ['name', 'email']

    def to_representation(self, obj):
        return add_key_prefix(self, obj, "recipient")


class EmailPickLeaderSerializer(serializers.ModelSerializer[AuthUser]):
    class Meta:
        model = AuthUser
        fields = ['name', 'email']

    def to_representation(self, obj):
        return add_key_prefix(self, obj, "pickleader")


class EmailPropertySerializer(serializers.ModelSerializer[Property]):
    class Meta:
        model = Property
        fields = ['id', 'address', 'owner']

    owner = serializers.ReadOnlyField(source='owner_name')
    address = serializers.ReadOnlyField(source='short_address')

    def to_representation(self, obj):
        return add_key_prefix(self, obj, "property")


class EmailCommentSerializer(serializers.ModelSerializer[Comment]):
    class Meta:
        model = Comment
        fields = ['author', 'content', 'date', 'time']

    date = serializers.DateTimeField(
        source='date_created',
        format='%Y-%m-%d',
    )
    time = serializers.DateTimeField(
        source='date_created',
        format='%H:%M %p',
    )
    author = serializers.ReadOnlyField(source='author.name')

    def to_representation(self, obj):
        return add_key_prefix(self, obj, "comment")


class EmailHarvestSerializer(serializers.ModelSerializer[Harvest]):
    class Meta:
        model = Harvest
        fields = ['id', 'public', 'date', 'url']

    public = serializers.ReadOnlyField(
        source='get_public_title'
    )
    date = serializers.DateTimeField(
        source='date_created',
        format='%Y-%m-%d',
    )
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return DOMAIN_NAME + reverse_lazy('harvest-detail', kwargs={'pk': obj.id})

    def to_representation(self, obj):
        return add_key_prefix(self, obj, "harvest")


class EmailRFPSerializer(serializers.ModelSerializer[RequestForParticipation]):
    class Meta:
        model = RequestForParticipation
        fields = ['name', 'email', 'comment', 'number_of_pickers']

    name = serializers.ReadOnlyField(source='person.name')
    email = serializers.ReadOnlyField(source='person.email')

    def to_representation(self, obj):
        return add_key_prefix(self, obj, "rfp")
