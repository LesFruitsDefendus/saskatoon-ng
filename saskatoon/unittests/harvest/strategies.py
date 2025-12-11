from hypothesis import strategies as st
from hypothesis.extra.django import from_model

import unittests.member.strategies as member_st
from member.models import Country, State, City, Neighborhood
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


property = from_model(
    Property,
    owner=st.just(None),
    neighborhood=from_model(Neighborhood),
    city=from_model(City),
    state=from_model(State),
    country=from_model(Country),
    changed_by=st.just(None),
)
equipment = from_model(
    Equipment,
    owner=st.just(None),
    property=st.just(None),
    type=from_model(EquipmentType),
)
harvest = from_model(
    Harvest,
    property=st.just(None),
    pick_leader=st.just(None),
    changed_by=st.just(None),
)
harvest_yield = from_model(
    HarvestYield,
    harvest=harvest,
    tree=from_model(TreeType),
    recipient=member_st.actor,
)
comment = from_model(Comment, author=member_st.auth_user, harvest=harvest)

request_for_participation = from_model(
    RequestForParticipation, harvest=harvest, person=member_st.person
)

# not sure how to generate images yet
# harvest_image = from_model(HarvestImage, harvest=harvest)
# property_image = from_model(PropertyImage, property=property)
