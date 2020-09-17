# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='election',
            options={'ordering': ['ordre', 'libelle']},
        ),
        migrations.AddField(
            model_name='election',
            name='ordre',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
