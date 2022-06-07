import imp
from django.contrib import admin
from .models import Profile, Message, User, Report, Artist, Track, Album, ArtistInReport, AlbumInReport, TrackInReport
from .forms import ProfileForm

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name')
    form = ProfileForm

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'text', 'created_at')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'last_fm_profile')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_fm_profile', 'created_at')

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'artist')

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'artist')

@admin.register(ArtistInReport)
class ArtistInReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'artist', 'report', 'scrobbles')

@admin.register(TrackInReport)
class TrackInReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'track', 'report', 'scrobbles')

@admin.register(AlbumInReport)
class AlbumInReport(admin.ModelAdmin):
    list_display = ('id', 'album', 'report', 'scrobbles')