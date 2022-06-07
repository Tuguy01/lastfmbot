from ast import Call
from cmath import log
from distutils.log import Log
from itertools import count
from mmap import MADV_DOFORK
from pdb import find_function
import profile
import requests
import json
from pydoc import text
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, ReplyKeyboardRemove, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, ConversationHandler
from telegram.utils.request import Request

from bot.models import Profile, Message, User, Report, Artist, Album, Track, AlbumInReport, ArtistInReport, TrackInReport

AUTORISATION = 0
CHOOSING_REPORT = 1




def log_errors(f):

    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e
    return inner






#Получение нового отчёта

@log_errors
def weekly_artists(account_name, report):
    url = "http://ws.audioscrobbler.com/2.0/?method=user.getweeklyartistchart&user=" + account_name + "&api_key=" + settings.LAST_FM_API_KEY + "&format=json"

    response = requests.get(url)
    json_data = json.loads(response.text)

    artists_all = len(json_data['weeklyartistchart']['artist'])
    artist_count = min(5, artists_all)

    text = "Ваши топ-исполнители за неделю:\n\n"
    for i in range (0, artists_all):

        if i < artist_count:
            text += str(i + 1) + ". " + json_data['weeklyartistchart']['artist'][i]['name'] + "      " + str(json_data['weeklyartistchart']['artist'][i]['playcount']) + " times last week.\n"

        artist, _ = Artist.objects.get_or_create(
            name = json_data['weeklyartistchart']['artist'][i]['name'],
        )
        artist_in_report = ArtistInReport(
            artist=artist,
            report=report,
            scrobbles=json_data['weeklyartistchart']['artist'][i]['playcount'],
        )
        artist_in_report.save()
        
    text += "\n"

    return text

@log_errors
def weekly_albums(account_name, report):
    url = "http://ws.audioscrobbler.com/2.0/?method=user.getweeklyalbumchart&user=" + account_name + "&api_key=" + settings.LAST_FM_API_KEY + "&format=json"

    response = requests.get(url)
    json_data = json.loads(response.text)

    albums_all = len(json_data['weeklyalbumchart']['album'])
    album_count = min(5, albums_all)

    text = "Ваши топ-альбомы за неделю:\n\n"
    for i in range (0, albums_all):

        if i < album_count:
            text += str(i + 1) + ". " + json_data['weeklyalbumchart']['album'][i]['name'] + "   by   " + json_data['weeklyalbumchart']['album'][i]['artist']['#text'] + "      " + str(json_data['weeklyalbumchart']['album'][i]['playcount']) + " times last week.\n"

        artist, _ = Artist.objects.get_or_create(
            name=json_data['weeklyalbumchart']['album'][i]['artist']['#text'],
        )
        album, _ = Album.objects.get_or_create(
            name=json_data['weeklyalbumchart']['album'][i]['name'],
            artist=artist,
        )
        album_in_report = AlbumInReport(
            album=album,
            report=report,
            scrobbles=json_data['weeklyalbumchart']['album'][i]['playcount'],
        )
        album_in_report.save()

    text += "\n"

    return text

@log_errors
def weekly_tracks(account_name, report):
    url = "http://ws.audioscrobbler.com/2.0/?method=user.getweeklytrackchart&user=" + account_name + "&api_key=" + settings.LAST_FM_API_KEY + "&format=json"

    response = requests.get(url)
    json_data = json.loads(response.text)

    tracks_all = len(json_data['weeklytrackchart']['track'])
    track_count = min(5, tracks_all)

    text = "Ваши топ-треки за неделю:\n\n"
    for i in range (0, tracks_all):

        if i < track_count:
            text += str(i + 1) + ". " + json_data['weeklytrackchart']['track'][i]['name'] + "   by   " + json_data['weeklytrackchart']['track'][i]['artist']['#text'] + "      " + str(json_data['weeklytrackchart']['track'][i]['playcount']) + " times last week.\n"

        artist, _ = Artist.objects.get_or_create(
            name=json_data['weeklytrackchart']['track'][i]['artist']['#text'],
        )
        track, _ = Track.objects.get_or_create(
            name=json_data['weeklytrackchart']['track'][i]['name'],
            artist=artist,
        )
        tarck_in_report = TrackInReport(
            track=track,
            report=report,
            scrobbles=json_data['weeklytrackchart']['track'][i]['playcount'],
        )
        tarck_in_report.save()
    return text



@log_errors
def get_report(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()
    account = User.objects.get(profile_id=p)
    account_name = account.last_fm_profile
    report = Report(
        last_fm_profile=account,
    )
    report.save()

    reply_text = weekly_artists(account_name, report)
    reply_text += weekly_albums(account_name, report)
    reply_text += weekly_tracks(account_name, report)

    update.message.reply_text(
        text=f'Отчёт для пользователя {account_name}:\n\n\n' + reply_text,
    )






#Получение топов за всё время

@log_errors
def top_artists(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()
    account = User.objects.get(profile_id=p)
    account_name = account.last_fm_profile

    url = "http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=" + account_name + "&api_key=" + settings.LAST_FM_API_KEY + "&format=json"

    response = requests.get(url)
    json_data = json.loads(response.text)

    artists_all = len(json_data['topartists']['artist'])
    artist_count = min(20, artists_all)

    reply_text = "Ваши топ-исполнители за всё время:\n\n"
    for i in range (0, artists_all):

        if i < artist_count:
            reply_text += str(i + 1) + ". " + json_data['topartists']['artist'][i]['name'] + "      " + str(json_data['topartists']['artist'][i]['playcount']) + " scrobbles.\n"

        artist, _ = Artist.objects.get_or_create(
            name=json_data['topartists']['artist'][i]['name'],
        )

    update.message.reply_text(
        text=reply_text,
    )

@log_errors
def top_albums(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()
    account = User.objects.get(profile_id=p)
    account_name = account.last_fm_profile

    url = "http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user=" + account_name + "&api_key=" + settings.LAST_FM_API_KEY + "&format=json"

    response = requests.get(url)
    json_data = json.loads(response.text)

    albums_all = len(json_data['topalbums']['album'])
    album_count = min(20, albums_all)

    reply_text = "Ваши топ-альбомы за всё время:\n\n"
    for i in range (0, albums_all):

        if i < album_count:
            reply_text += str(i + 1) + ". " + json_data['topalbums']['album'][i]['name'] + "   by   " + json_data['topalbums']['album'][i]['artist']['name'] + "      " + str(json_data['topalbums']['album'][i]['playcount']) + " scrobbles.\n"

        artist, _ = Artist.objects.get_or_create(
            name=json_data['topalbums']['album'][i]['artist']['name'],
        )
        album, _ = Album.objects.get_or_create(
            name=json_data['topalbums']['album'][i]['name'],
            artist=artist,
        )

    update.message.reply_text(
        text=reply_text,
    )

@log_errors
def top_tracks(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()
    account = User.objects.get(profile_id=p)
    account_name = account.last_fm_profile

    url = "http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user=" + account_name + "&api_key=" + settings.LAST_FM_API_KEY + "&format=json"

    response = requests.get(url)
    json_data = json.loads(response.text)

    tracks_all = len(json_data['toptracks']['track'])
    track_count = min(20, tracks_all)

    reply_text = "Ваши топ-треки за всё время:\n\n"
    for i in range (0, tracks_all):

        if i < track_count:
            reply_text += str(i + 1) + ". " + json_data['toptracks']['track'][i]['name'] + "   by   " + json_data['toptracks']['track'][i]['artist']['name'] + "      " + str(json_data['toptracks']['track'][i]['playcount']) + " scrobbles.\n"

        artist, _ = Artist.objects.get_or_create(
            name=json_data['toptracks']['track'][i]['artist']['name'],
        )
        track, _ = Track.objects.get_or_create(
            name=json_data['toptracks']['track'][i]['name'],
            artist=artist,
        )

    update.message.reply_text(
        text=reply_text,
    )




#Привязка аккаунта

@log_errors
def set_profile(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()
    update.message.reply_text(
        'Введите имя аккуанта на last.fm:',
        reply_markup=ReplyKeyboardRemove(),
    )
    return AUTORISATION

@log_errors
def name_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    account_name = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )

    u = User(
        profile = p,
        last_fm_profile = account_name,
    )
    u.save()
    m = Message(
        profile=p,
        text=account_name,
    )
    m.save()

    update.message.reply_text(
        text=f'Аккаунт {account_name} успешно привязан к вашему профилю',
    )
    return ConversationHandler.END

@log_errors
def cancel_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()
    update.message.reply_text(
        text=f'Отмена привязки аккаунта last.fm'
    )
    return ConversationHandler.END









#Получение недавних треков

@log_errors
def recent_tracks(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()
    account = User.objects.get(profile_id=p)
    account_name = account.last_fm_profile

    url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + account_name + "&api_key=" + settings.LAST_FM_API_KEY + "&format=json"

    response = requests.get(url)
    json_data = json.loads(response.text)

    tracks_all = len(json_data['recenttracks']['track'])
    track_count = min(20, tracks_all)

    reply_text = "Ваши последние треки:\n\n"
    for i in range (0, tracks_all):

        if i < track_count:
            reply_text += json_data['recenttracks']['track'][i]['name'] + "   by   " + json_data['recenttracks']['track'][i]['artist']['#text'] + "\n"

        artist, _ = Artist.objects.get_or_create(
            name=json_data['recenttracks']['track'][i]['artist']['#text'],
        )
        track, _ = Track.objects.get_or_create(
            name=json_data['recenttracks']['track'][i]['name'],
            artist=artist,
        )

    update.message.reply_text(
        text=reply_text,
    )








#Загрузка отчёта из бд

@log_errors
def load_artists(report):

    artists_in_report = ArtistInReport.objects.filter(report_id=report).order_by("-scrobbles")[:5]

    artists_all = artists_in_report.count()
    artist_count = min(5, artists_all)

    text = "Ваши топ-артисты:\n\n"
    for i in range (0, artist_count):
        artist = Artist.objects.get(id=artists_in_report[i].artist_id)
        text += str(i + 1) + ". " + artist.name + "      " + str(artists_in_report[i].scrobbles) + " scrobbles\n"

    return text + "\n"

@log_errors
def load_albums(report):

    albums_in_report = AlbumInReport.objects.filter(report_id=report).order_by("-scrobbles")[:5]

    albums_all = albums_in_report.count()
    album_count = min(5, albums_all)

    text = "Ваши топ-альбомы:\n\n"
    for i in range (0, album_count):
        album = Album.objects.get(id=albums_in_report[i].album_id)
        artist = Artist.objects.get(id=album.artist_id)
        text += str(i + 1) + ". " + album.name + "   by   " + artist.name + "      " + str(albums_in_report[i].scrobbles) + " scrobbles\n"

    return text + "\n"

@log_errors
def load_tracks(report):

    tracks_in_report = TrackInReport.objects.filter(report_id=report).order_by("-scrobbles")[:5]

    tracks_all = tracks_in_report.count()
    track_count = min(5, tracks_all)

    text = "Ваши топ-треки:\n\n"
    for i in range (0, track_count):
        track = Track.objects.get(id=tracks_in_report[i].track_id)
        artist = Artist.objects.get(id=track.artist_id)
        text += str(i + 1) + ". " + track.name + "   by   " + artist.name + "      " + str(tracks_in_report[i].scrobbles) + " scrobbles\n"

    return text


@log_errors
def load_report(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()

    account = User.objects.get(profile_id=p)
    user_reports = Report.objects.filter(last_fm_profile_id=account.id).order_by("-created_at")[:10]

    reports_all = user_reports.count()
    report_count = min(10, reports_all)

    text = "Ваши последние отчёты:\n"
    for i in range (0, reports_all):
        time = user_reports[i].created_at
        if i < report_count:
            text += str(i + 1) + ". " + "Отчёт от " + str(time) + "\n"
    
    text += "\n\nВыберите номер отчёта из списка"

    update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardRemove(),
    )
    return CHOOSING_REPORT

@log_errors
def report_choosing(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()

    account = User.objects.get(profile_id=p)
    user_reports = Report.objects.filter(last_fm_profile_id=account.id).order_by("-created_at")[:10]

    reports_all = user_reports.count()
    report_count = min(10, reports_all)

    if input_text.isdigit == False:
        update.message.reply_text(
            text=f'Некорректный номер отчёта',
        )
        return ConversationHandler.END

    if int(input_text) < 1 or int(input_text) > report_count:
        update.message.reply_text(
            text=f'Некорректный номер отчёта',
        )
        return ConversationHandler.END

    reply_text = "Содержимое выбранного отчёта:\n\n"
    reply_text += load_artists(user_reports[int(input_text) - 1])
    reply_text += load_albums(user_reports[int(input_text) - 1])
    reply_text += load_tracks(user_reports[int(input_text) - 1])

    update.message.reply_text(
        text=reply_text,
    )
    return ConversationHandler.END

@log_errors
def back_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    input_text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    m = Message(
        profile=p,
        text=input_text,
    )
    m.save()
    update.message.reply_text(
        text=f'Выбор отчёта отменён'
    )
    return ConversationHandler.END










#Ответ на текстовое сооббщение

@log_errors
def answer(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Простите, я вас не понимаю, используйте комманды из меню",
    )

class Command(BaseCommand):

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot=Bot(
            request=request,
            token=settings.TOKEN,
        )
        print(bot.get_me())

        updater = Updater(
            bot=bot,
            use_context=True,
        )

        main_handler = ConversationHandler(
            entry_points=[
                CommandHandler('set_profile', set_profile),
            ],
            states={
                AUTORISATION:[
                    CommandHandler('cancel', cancel_handler),
                    MessageHandler(Filters.all, name_handler, pass_user_data=True),
                ]
            },
            fallbacks=[],
        )

        loading_handler = ConversationHandler(
            entry_points=[
                CommandHandler('load_report', load_report),
            ],
            states={
                CHOOSING_REPORT:[
                    CommandHandler('back', back_handler),
                    MessageHandler(Filters.all, report_choosing, pass_user_data=True),
                ]
            },
            fallbacks=[],
        )

        updater.dispatcher.add_handler(main_handler)
        updater.dispatcher.add_handler(loading_handler)

        updater.dispatcher.add_handler(CommandHandler('get_report', get_report))
        updater.dispatcher.add_handler(CommandHandler('top_artists', top_artists))
        updater.dispatcher.add_handler(CommandHandler('top_albums', top_albums))
        updater.dispatcher.add_handler(CommandHandler('top_tracks', top_tracks))
        updater.dispatcher.add_handler(CommandHandler('get_recent_tracks', recent_tracks))
        updater.dispatcher.add_handler(MessageHandler(Filters.text, answer))


        updater.start_polling()
        updater.idle()