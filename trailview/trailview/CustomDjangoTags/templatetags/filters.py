# custom filters for Trail View

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def catNum(value, arg):
    return value + str(arg)
