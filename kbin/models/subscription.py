from django.db import models
from .user import User
from .magazine import Magazine


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE)

    unique_together = ('user', 'magazine')
