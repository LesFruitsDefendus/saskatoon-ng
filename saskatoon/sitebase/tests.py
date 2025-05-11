
from logging import getLogger
from typing import Optional

from harvest.models import Harvest, Property
from member.models import Person

logger = getLogger('saskatoon')


def get_test_owner_person() -> Optional[Person]:
    try:
        return Person.objects.get(first_name='TEST', family_name='OWNER')
    except Person.DoesNotExist:
        logger.warning("Could not find test owner")
        return None


def get_test_property() -> Optional[Property]:
    test_owner = get_test_owner_person()
    print(test_owner, test_owner is not None)
    if test_owner is not None:
        try:
            return Property.objects.get(owner=test_owner)
        except Property.DoesNotExist:
            logger.warning("Could not find test property")

    return None


def get_test_harvest() -> Optional[Harvest]:
    test_property = get_test_property()

    if test_property is not None:
        qs = Harvest.objects.filter(property=test_property, pick_leader__isnull=False)
        if qs.exists():
            return qs.first()

        logger.warning("Could not find a test harvest with pickleader.")

    return None
