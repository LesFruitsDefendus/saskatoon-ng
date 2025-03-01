from rest_framework import serializers
from harvest.models import Harvest, Comment, Property
from member.models import AuthUser


class EmailPickLeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['name', 'email']


class EmailPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'address']

    address = serializers.ReadOnlyField(
        source='short_address'
    )


class EmailCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['author', 'content', 'date', 'time']

    date = serializers.DateTimeField(
        source='date_created',
        format='%b %d',
    )

    time = serializers.DateTimeField(
        source='date_created',
        format='%H:%M',
    )


class EmailHarvestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvest
        fields = ['id', 'anouncement', 'pick_leader', 'comment']

    anouncement = serializers.ReadOnlyField(
        source='get_public_title'
    )

    pick_leader = EmailPickLeaderSerializer(
        many=False,
        read_only=True
    )

    comment = serializers.SerializerMethodField()

    def get_comment(self, obj):
        return EmailCommentSerializer(obj.comments.last()).data
