from cgitb import text
from operator import mod
import profile
from tabnanny import verbose
from django.db import models

class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя бота',
        unique=True,
    )
    name = models.TextField(
        verbose_name='Ник пользователя',
    )

    def __str__(self):
        return f'#{self.external_id} {self.name}'
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

class Message(models.Model):
    profile = models.ForeignKey(
        to='bot.Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )

    text = models.TextField(
        verbose_name='Текст',
    )

    created_at = models.DateTimeField(
        verbose_name='Время получения',
        auto_now_add=True,
    )

    def __str__(self):
        return f'Сообщение {self.pk} от {self.profile}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

class User(models.Model):
    profile = models.ForeignKey(
        to='bot.Profile',
        verbose_name='Профиль в Телеграме',
        on_delete=models.PROTECT,
        unique=True,
    )

    last_fm_profile = models.TextField(
        verbose_name='Имя профиля на last.fm',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Report(models.Model):
    last_fm_profile = models.ForeignKey(
        to='bot.User',
        on_delete=models.PROTECT,
    )

    created_at = models.DateTimeField(
        verbose_name='Время получения',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Отчёт'
        verbose_name_plural = 'Отчёты'

class Artist(models.Model):
    name = models.TextField(
        verbose_name='Имя исполнителя',
    )

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'

class Track(models.Model):
    name = models.TextField(
        verbose_name='Название трека',
    )

    artist = models.ForeignKey(
        to='bot.Artist',
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'

class Album(models.Model):
    name = models.TextField(
        verbose_name='Название альбома',
    )

    artist = models.ForeignKey(
        to='bot.Artist',
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'

class ArtistInReport(models.Model):
    artist = models.ForeignKey(
        to='bot.Artist',
        on_delete=models.PROTECT,
    )

    report = models.ForeignKey(
        to='bot.Report',
        on_delete=models.PROTECT,
    )

    scrobbles = models.IntegerField(
        verbose_name='Прослушиваний в отчёте',
        default=0,
    )

    class Meta:
        verbose_name = 'Исполнитель в отчёте'
        verbose_name_plural = 'Исполнители в отчёте'

class TrackInReport(models.Model):
    track = models.ForeignKey(
        to='bot.Track',
        on_delete=models.PROTECT,
    )

    report = models.ForeignKey(
        to='bot.Report',
        on_delete=models.PROTECT,
    )

    scrobbles = models.IntegerField(
        verbose_name='Прослушиваний в отчёте',
        default=0,
    )

    class Meta:
        verbose_name = 'Трек в отчёте'
        verbose_name_plural = 'Треки в отчёте'

class AlbumInReport(models.Model):
    album = models.ForeignKey(
        to='bot.Album',
        on_delete=models.PROTECT,
    )

    report = models.ForeignKey(
        to='bot.Report',
        on_delete=models.PROTECT,
    )

    scrobbles = models.IntegerField(
        verbose_name='Прослушиваний в отчёте',
        default=0,
    )

    class Meta:
        verbose_name = 'Альбом в отчёте'
        verbose_name_plural = 'Альбомы в отчёте'