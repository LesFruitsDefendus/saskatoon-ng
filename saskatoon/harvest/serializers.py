from rest_framework import serializers
from harvest.models import Harvest

# Harvest serializer
class HarvestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvest
        fields = '__all__'
