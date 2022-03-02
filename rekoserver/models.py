from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class People(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)


class Movies(models.Model):
    id = models.IntegerField(primary_key=True)
    imdb_id = models.CharField(max_length=32, null=True)
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, null=True)
    backdrop_path = models.CharField(max_length=255, null=True)
    release_date = models.IntegerField()
    genres = ArrayField(models.CharField(max_length=255))
    keywords = ArrayField(models.CharField(max_length=255))
    credits = ArrayField(models.IntegerField())


class Watched(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    m_id = models.ForeignKey(
        Movies,
        on_delete=models.CASCADE
    )
    rating = models.IntegerField()
