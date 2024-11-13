# Generated by Django 5.1.1 on 2024-11-04 02:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NinerCreations', '0003_room_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='NinerCreations.post'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='action',
            field=models.CharField(choices=[('CREATED_ROOM', 'Created a Room'), ('CREATED_POST', 'Created a Post')], max_length=20),
        ),
    ]