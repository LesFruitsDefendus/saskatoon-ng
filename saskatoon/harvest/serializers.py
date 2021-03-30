from rest_framework import serializers
from .models import Harvest, Property, Equipment, EquipmentType, RequestForParticipation
from member.models import Neighborhood

# Neighborhood serializer
class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = '__all__'

# Property serializer
class PropertySerializer(serializers.ModelSerializer):
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)
    title = serializers.ReadOnlyField(source="__str__")
    harvests = serializers.ReadOnlyField(source="get_harvests")
    last_succeeded_harvest = serializers.ReadOnlyField(source="get_last_succeeded_harvest")
    trees = serializers.StringRelatedField(many=True)
    class Meta:
        model = Property
        fields = '__all__'

# Property info serializer
# This is needed for HarvestSerializer
class PropertyInfoSerializer(serializers.ModelSerializer):
    neighborhood = NeighborhoodSerializer(many=False, read_only=True)
    title = serializers.ReadOnlyField(source="__str__")
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
    class Meta:
        model = Equipment
        fields = '__all__'

# Harvest serializer
class HarvestSerializer(serializers.ModelSerializer):

    # three different ways of getting a multimodel serializer:
    # 1) calling a model method
    pickers = serializers.ReadOnlyField(source='get_pickers')
    start_date = serializers.DateTimeField(format="%Y-%m-%d")
    start_time = serializers.DateTimeField(source='start_date', format="%H:%M")
    # # 2) get string rather than id from a pk
    pick_leader = serializers.StringRelatedField(many=False)
    trees = serializers.StringRelatedField(many=True)
    # 3) get the full instance from another serializer class
    property = PropertyInfoSerializer(many=False, read_only=True)

    class Meta:
        model = Harvest
        fields = '__all__'
