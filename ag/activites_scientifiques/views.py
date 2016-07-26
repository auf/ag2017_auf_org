# -*- encoding: utf-8 -*-
from ag.activites_scientifiques.forms import LoginForm, PickForm
from ag.gestion.models import Participant, ActiviteScientifique
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect


def login(request):
    if request.method == 'GET':
        login_form = LoginForm()
    else:
        assert request.method == 'POST'
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            adresse_courriel = login_form.cleaned_data['email']
            try:
                participant = Participant.objects.get(
                    courriel=adresse_courriel)
            except Participant.DoesNotExist:
                return redirect(
                    '{0}?adresse_courriel={1}'.format(
                        reverse('act_sci_login_not_found'),
                        adresse_courriel)
                )
            request.session['act_sci_participant_id'] = str(participant.id)
            return redirect(reverse('act_sci_pick'))

    return render(request, 'activites_scientifiques/login.html',
                  {'login_form': login_form})


def pick(request):
    try:
        participant_id = int(request.session['act_sci_participant_id'])
        participant = Participant.objects.get(id=participant_id)
    except (KeyError, Participant.DoesNotExist):
        return redirect(reverse('act_sci_login'))
    just_saved = False
    if request.method == 'POST':
        activite_id = request.POST['activites']
        if activite_id:
            activite_choisie = ActiviteScientifique.objects.get(id=activite_id)
            participant.activite_scientifique = activite_choisie
            participant.save()
            just_saved = True
    return render(request, 'activites_scientifiques/pick.html', {
        # 'pick_form': pick_form,
        'participant': participant,
        'just_saved': just_saved,
        'activites': ActiviteScientifique.objects.all(),
    })


def logout(request):
    try:
        del request.session['act_sci_participant_id']
    except KeyError:
        pass
    return redirect(reverse('act_sci_login'))


def clear(request):
    try:
        participant_id = int(request.session['act_sci_participant_id'])
        participant = Participant.objects.get(id=participant_id)
    except (KeyError, Participant.DoesNotExist):
        return redirect(reverse('act_sci_login'))
    participant.activite_scientifique = None
    participant.save()
    return redirect(reverse('act_sci_pick'))