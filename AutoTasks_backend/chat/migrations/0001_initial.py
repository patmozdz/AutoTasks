# Generated by Django 5.0 on 2023-12-23 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_history', models.JSONField(default=list)),
                ('messages', models.JSONField(default=list)),
            ],
        ),
    ]
