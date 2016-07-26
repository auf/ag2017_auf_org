# -*- encoding: utf-8 -*-

from django import template

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
        value = u'Oui' if value else u'Non'
    elif not value:
        value = u'------'

    return {'label': label, 'value': value}
