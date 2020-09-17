# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recteur', models.CharField(max_length=200)),
                ('fonction', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('image', models.ImageField(null=True, upload_to=b'mot', blank=True)),
                ('date_pub', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Partenaire',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=200)),
                ('image', models.ImageField(null=True, upload_to=b'partenaire', blank=True)),
                ('lien', models.URLField()),
                ('date_pub', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(null=True, upload_to=b'slider', blank=True)),
                ('titre', models.CharField(max_length=250)),
                ('lien', models.CharField(max_length=200, null=True, blank=True)),
                ('date_pub', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titre', models.CharField(max_length=200)),
                ('video', models.TextField(null=True, verbose_name=b'Code de la video', blank=True)),
                ('description', models.TextField(null=True, verbose_name=b'Description de la video', blank=True)),
                ('date_pub', models.DateField()),
            ],
        ),
    ]
