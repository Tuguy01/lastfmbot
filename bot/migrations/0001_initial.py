# Generated by Django 4.0.4 on 2022-04-24 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.PositiveIntegerField(verbose_name='ID пользователя бота')),
                ('name', models.TextField(verbose_name='Ник пользователя')),
            ],
            options={
                'verbose_name': 'Профиль',
            },
        ),
    ]
