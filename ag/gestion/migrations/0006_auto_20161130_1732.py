# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0005_auto_20161127_1804'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='institution',
            options={'ordering': ('nom',)},
        ),
        migrations.RemoveField(
            model_name='participant',
            name='region',
        ),
        migrations.AddField(
            model_name='participant',
            name='implantation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    blank=True, to='reference.Implantation',
                                    null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='fonction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    blank=True, to='gestion.Fonction',
                                    null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    blank=True, to='gestion.Institution',
                                    null=True),
        ),
    ]
