from django.db import models
from .user import User
from django.utils import timezone
from .thread import *


class Comment(models.Model):
    # Automaticament, si no s'especifica, django genera un id (int) com a PK

    # En cas que l'author associat s'elimini, tots el threads seus s'elimines
    author = models.ForeignKey(User, on_delete=models.CASCADE, default='default_user')
    body = models.TextField(max_length=35000, null=True)
    creation_data = models.DateTimeField(default=timezone.now)
    last_edited = models.DateTimeField(null=True)
    # Rang dels likes [0-2147483647]
    num_likes = models.PositiveIntegerField(default=0)
    num_dislikes = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    # En cas que el thread associat s'elimini, tots els seus comentaris s'eliminen
    thread = models.ForeignKey(Publicacio, on_delete=models.CASCADE, default='default_thread')
