from django.apps import apps
from django.db import models
from .user import User
from django.utils import timezone



class Magazine(models.Model):
    # Creador de la magazine
    author = models.ForeignKey(User, on_delete=models.CASCADE, default='default_user')
    # data de creacio
    creation_date = models.DateTimeField(default=timezone.now)

    # info de creació
    name = models.CharField(unique=True, max_length=25000)
    title = models.CharField(max_length=50000)
    description = models.TextField(max_length=40000, null=True)
    rules = models.TextField(max_length=10000, null=True)
    nsfw = models.BooleanField(null=True)

    # info estadística
    n_threads = models.PositiveIntegerField(default=0)
    n_links = models.PositiveIntegerField(default=0)
    n_elements = models.PositiveIntegerField(default=0)
    n_suscriptions = models.PositiveIntegerField(default=0)

    def total_comments(self):
        return sum(publicacio.num_coments for publicacio in self.publicacio_set.all())

    def total_publicacions(self):
        return self.publicacio_set.all().count()

    def total_threads(self):
        Thread = apps.get_model('kbin', 'Thread')
        print(Thread.objects.filter(magazine=self).count())
        return Thread.objects.filter(magazine=self).count()

    def total_links(self):
        Link = apps.get_model('kbin', 'Link')
        return Link.objects.filter(magazine=self).count()