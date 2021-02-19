from django.db import models


class Artist(models.Model):
    class Meta:
        db_table = 'artists'
        app_label = 'testapp'

    name = models.CharField(max_length=100, unique=True)
    genres = models.JSONField()
    members = models.PositiveIntegerField()


class Album(models.Model):
    class Meta:
        db_table = 'albums'
        app_label = 'testapp'

    class AlbumType(models.TextChoices):
        CD = 'cd', 'CD'
        VINYL = 'vinyl', 'Vinyl'

    title = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    type = models.CharField(choices=AlbumType.choices, max_length=10)
    metadata = models.JSONField(null=True)


class Song(models.Model):
    class Meta:
        db_table = 'songs'
        app_label = 'testapp'

    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')
    title = models.CharField(max_length=100)
    duration = models.DurationField(null=False)
    metadata = models.JSONField(null=False)
