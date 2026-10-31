from hypothesis import strategies as st
from hypothesis.extra.django import from_model, register_field_strategy
from phone_field import PhoneField
from django_quill.fields import QuillField

from member.models import (
    Country,
    State,
    City,
    Neighborhood,
    Actor,
    Person,
    AuthUser,
    Onboarding,
    Organization,
)


register_field_strategy(PhoneField, st.text(alphabet="0123456789"))
quill_strategy = st.just('{"delta": "", "html": "<p></p>"}')
register_field_strategy(QuillField, quill_strategy)
actor = from_model(Actor)
actor_id = actor.map(lambda a: a.actor_id)
person = from_model(
    Person,
    actor_ptr_id=actor_id,
    onboarding=from_model(Onboarding),
    neighborhood=from_model(Neighborhood),
    city=from_model(City),
    state=from_model(State),
    country=from_model(Country),
)
organization = from_model(
    Organization,
    actor_ptr_id=actor_id,
    contact_person=st.just(None),
    neighborhood=from_model(Neighborhood),
    city=from_model(City),
    state=from_model(State),
    country=from_model(Country),
)

auth_user = from_model(AuthUser, person=person)
