from django.apps import apps
from django.db import models


class User(models.Model):
    # Podem definir el maxim de caracters de username
    username = models.CharField(max_length=32, primary_key=True)
    description = models.TextField(default="", max_length=10000)
    cover = models.ImageField(default="", max_length=10000)
    avatar = models.ImageField(default="", max_length=10000)
    email = models.EmailField(unique=True)
    api_key = models.CharField(max_length=100, blank=True, null=True, unique=True)

    @property
    def total_threads(self):
        publicacio = apps.get_model('kbin', 'Publicacio')
        return publicacio.objects.filter(author=self.username).count()

    @property
    def total_comments(self):
        comment = apps.get_model('kbin', 'Comment')
        return comment.objects.filter(author=self.username).count()

    @property
    def total_boosts(self):
        boost = apps.get_model('kbin', 'Boost')
        return boost.objects.filter(user=self.username).count()
