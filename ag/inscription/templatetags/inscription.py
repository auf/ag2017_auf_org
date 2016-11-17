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


def adresse_email_region(code_region):
    return u"AG2017.B{}@auf.org".format(code_region)


@register.simple_tag(takes_context=True)
def email_region(context, subject=u""):
    if subject:
        subject = u"?subject={}".format(subject)
    code_region = context["inscription"].get_region().code
    adresse_region = adresse_email_region(code_region)
    return mark_safe(
        u'<a href="mailto:{adresse_region}{subject}">'
        u'{adresse_region}</a>'.format(
            adresse_region=adresse_region,
            subject=subject)
    )


@register.simple_tag()
def unicode_checkbox(checked):
    s = u'&#x2611;' if checked else u'&#x2610;'
    return mark_safe(s)
