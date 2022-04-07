
from re import sub
from django.db.models import Q
from harvest.models import Property
from member.models import AuthUser, Person


def get_similar_properties(pending_property):
    """Look for potential property/owner duplicates

    TO BE IMPROVED
    - pending_contact_name needs to be split into 2 separate fields
    - pending_contact_phone should be formatted properly upon form saving
    """

    p = pending_property
    if not p.pending:
        return Property.objects.none()

    query = Q()
    try:
        email = p.pending_contact_email
        if email:
            query |= Q(owner__person__auth_user__email=email)

        name = p.pending_contact_name  # TODO split contact_name into first/last names
        if name:
            pass
            # query |= Q(owner__person__first_name__icontains=first_name)
            # query |= Q(owner__person__last_name__icontains=last_name)

        phone = p.pending_contact_phone
        if phone:
            query |= Q(owner__person__phone=phone)

        # address match
        q0 = Q(street__icontains=p.street)
        q1 = Q(street_number__icontains=p.street_number)
        q2 = Q(postal_code__icontains=p.postal_code)
        q3 = Q(neighborhood=p.neighborhood)
        query |= q0 & q1 & (q2 | q3)  # TODO adjust, might be too stringent

        return Property.objects.filter(query).exclude(id=p.id).distinct()

    except Exception as _e:
        print("Can't find similar properties for %s: %s (%s)", p, str(_e), type(_e))
        return Property.objects.none()
