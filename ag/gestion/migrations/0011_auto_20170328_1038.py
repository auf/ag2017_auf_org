# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0010_auto_20170308_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='suppleant_de',
            field=models.OneToOneField(related_name='suppleant', null=True, on_delete=django.db.models.deletion.PROTECT, blank=True, to='gestion.Participant'),
        ),
    ]
