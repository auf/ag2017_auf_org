# -*- encoding: utf-8 -*-

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag('gestion/champ_fiche.html')
def champ_fiche(form, field_name):
    label = form.fields[field_name].label
    participant = form.get_participant()
    if hasattr(participant, 'get_' + field_name + '_display'):
        display_func = getattr(participant, 'get_' + field_name + '_display')
        value = display_func()
    elif hasattr(participant, field_name):
        value = getattr(participant, field_name)
    elif field_name in form.initial:
        value = form.initial[field_name]
    else:
        value = None
    if isinstance(value, bool):
        value = 'Oui' if value else 'Non'
    elif not value:
        value = '------'

    return {'label': label, 'value': value}


@register.filter
def sum_data(data):
    return mark_safe('<a href="{}">{}</a>'.format(data.search_url,
                                                   data.sum))
