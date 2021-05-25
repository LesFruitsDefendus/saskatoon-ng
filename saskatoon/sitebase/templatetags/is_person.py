from django import template

register = template.Library()

@register.filter
def is_person(actor):
    try:
        # trying to access person will throw an exception
        # if the actor is an organization
        actor.person
        return True
    except:
        return False
