# Generated by Django 4.2.5 on 2023-10-06 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_knowledge_scene_scenenpc_scenerunner_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scenerunner',
            old_name='npcs',
            new_name='scene',
        ),
    ]
