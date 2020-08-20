from enum import Enum

from django.db import models
from django_enum_choices.fields import EnumChoiceField


class Artist(models.Model):
    class Meta:
        db_table = 'artists'
        app_label = 'testapp'

    name = models.CharField(max_length=100)
    genders = models.JSONField(models.CharField(max_length=30))
    members = models.PositiveIntegerField()


class Album(models.Model):
    class Meta:
        db_table = 'albums'
        app_label = 'testapp'

    class AlbumType(Enum):
        CD = 'cd'
        VINYL = 'vinyl'

    title = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    type = EnumChoiceField(AlbumType)
    metadata = models.JSONField(null=True)


class Song(models.Model):
    class Meta:
        db_table = 'songs'
        app_label = 'testapp'

    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')
    title = models.CharField(max_length=100)
    duration = models.DurationField(null=False)
    metadata = models.JSONField(null=False)
