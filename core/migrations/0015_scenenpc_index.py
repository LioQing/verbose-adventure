# Generated by Django 4.2.5 on 2023-10-07 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_rename_npcs_scenerunner_scene'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenenpc',
            name='index',
            field=models.PositiveIntegerField(default=0),
        ),
    ]