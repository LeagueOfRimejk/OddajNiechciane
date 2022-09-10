from django import template

register = template.Library()


@register.filter
def in_range(number):
    return range(number)
