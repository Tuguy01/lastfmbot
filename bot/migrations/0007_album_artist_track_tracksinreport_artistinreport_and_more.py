# Generated by Django 4.0.4 on 2022-05-22 07:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_alter_user_profile_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название альбома')),
            ],
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Имя исполнителя')),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название трека')),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.artist')),
            ],
        ),
        migrations.CreateModel(
            name='TracksInReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.report')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.track')),
            ],
        ),
        migrations.CreateModel(
            name='ArtistInReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.artist')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.report')),
            ],
        ),
        migrations.CreateModel(
            name='ALbumsInReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.album')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.report')),
            ],
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bot.artist'),
        ),
    ]
