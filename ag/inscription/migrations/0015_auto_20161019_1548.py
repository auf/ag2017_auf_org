# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0014_auto_20161019_1200'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inscription',
            old_name='identite_confirmee',
            new_name='identite_accompagnateur_confirmee',
        ),
        migrations.AddField(
            model_name='inscription',
            name='atteste_pha',
            field=models.CharField(max_length=1, null=True, choices=[(b'P', "J'atteste \xeatre la plus haute autorit\xe9 de mon \xe9tablissement et participerai \xe0 la 17\xe8me Assembl\xe9e g\xe9n\xe9rale de l'AUF"), (b'R', "J'atteste \xeatre le repr\xe9sentant d\xfbment mandat\xe9 par la plus haute autorit\xe9 de mon \xe9tablissement pour participer \xe0 la 17\xe8me Assembl\xe9e g\xe9n\xe9rale de l'AUF")]),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='paiement',
            field=models.CharField(blank=True, max_length=2, verbose_name='modalit\xe9s de paiement', choices=[(b'CB', 'Carte bancaire'), (b'VB', 'Virement bancaire'), (b'CE', 'Ch\xe8que en euros'), (b'DL', 'Devises locales')]),
        ),
    ]
