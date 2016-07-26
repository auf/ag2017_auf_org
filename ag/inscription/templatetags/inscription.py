# encoding: utf-8

from django import template

register = template.Library()


@register.inclusion_tag('inscription/checkbox.html')
def checkbox(field):
    return {'field': field}


@register.inclusion_tag('inscription/field.html')
def field(field):
    return {'field': field}


@register.inclusion_tag('inscription/inline_radio.html')
def inline_radio(field):
    return {'field': field}
