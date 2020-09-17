# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0002_auto_20161130_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='implantation_bureau',
            field=models.ForeignKey(related_name='gere_region', to='reference.Implantation', null=True),
        ),
    ]
