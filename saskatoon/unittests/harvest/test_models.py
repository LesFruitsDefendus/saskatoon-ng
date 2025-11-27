from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase, from_model

from harvest.models import (
    RequestForParticipation,
    Comment,
    Property,
    Harvest,
    HarvestYield,
    Equipment,
    EquipmentType,
    TreeType,
)
import unittests.harvest.strategies as harvest_st

settings.register_profile("fast", max_examples=50)

# any tests executed before loading this profile will still use the
# default active profile of 100 examples.

settings.load_profile("fast")


class TestTreeType(TestCase):
    @given(tree_type=from_model(TreeType))
    def test_can_be_created(self, tree_type):
        assert isinstance(tree_type, TreeType)


class TestProperty(TestCase):
    @given(property=harvest_st.property)
    def test_can_be_created(self, property):
        assert isinstance(property, Property)


class TestEquipmentType(TestCase):
    @given(equipment_type=from_model(EquipmentType))
    def test_can_be_created(self, equipment_type):
        assert isinstance(equipment_type, EquipmentType)


class TestEquipment(TestCase):
    @given(equipment=harvest_st.equipment)
    def test_can_be_created(self, equipment):
        assert isinstance(equipment, Equipment)


class TestHarvest(TestCase):
    @given(harvest=harvest_st.harvest)
    def test_can_be_created(self, harvest):
        assert isinstance(harvest, Harvest)

    @given(
        harvest=harvest_st.harvest,
        equipment=harvest_st.equipment,
        status=st.sampled_from(Harvest.Status),
    )
    def test_harvest_reservation_validation(self, harvest, equipment, status):
        """Test that status changes revalidate harvest reservations"""
        harvest.equipment_reserved.set([equipment])
        harvest.status = status
        harvest.save()

        valid_status = [Harvest.Status.SCHEDULED, Harvest.Status.READY, Harvest.Status.SUCCEEDED]
        count = harvest.equipment_reserved.values().count()

        if harvest.status in valid_status and status in valid_status:
            assert count == 1
        else:
            assert count == 0


class TestComment(TestCase):
    @given(comment=harvest_st.comment)
    def test_can_be_created(self, comment):
        assert isinstance(comment, Comment)


class TestHarvestYield(TestCase):
    @given(harvest_yield=harvest_st.harvest_yield)
    def test_can_be_created(self, harvest_yield):
        assert isinstance(harvest_yield, HarvestYield)


class TestRequestForParticipation(TestCase):
    @given(request=harvest_st.request_for_participation)
    def test_can_be_created(self, request):
        assert isinstance(request, RequestForParticipation)


# not sure how to generate images yet
# class TestHarvestImage(TestCase):
#    @given(image=harvest_st.harvest_image)
#    def test_can_be_created(self, image):
#        assert isinstance(image, HarvestImage)

# class TestPropertyImage(TestCase):
#    @given(image=harvest_st.property_image)
#    def test_can_be_created(self, image):
#        assert isinstance(image, PropertyImage)
settings.load_profile("default")
