from django import template

register = template.Library()

@register.filter
def is_iframe(request):
    return request.headers.get('Sec-Fetch-Dest') == "iframe"
