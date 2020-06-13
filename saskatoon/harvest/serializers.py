from rest_framework import serializers
from harvest.models import Harvest, Property

# Harvest serializer
class HarvestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvest
        fields = '__all__'

# Property serializer
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'
