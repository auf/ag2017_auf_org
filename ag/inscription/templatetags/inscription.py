# encoding: utf-8

from django import template
from django.utils.safestring import mark_safe

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


@register.simple_tag(takes_context=True)
def email_region(context, subject=u""):
    if subject:
        subject = u"?subject={}".format(subject)
    return mark_safe(
        u'<a href="mailto:ag2017.{region}@auf.org{subject}">'
        u'ag2017.{region}@auf.org</a>'.format(
            region=context["inscription"].get_region().code,
            subject=subject)
    )
