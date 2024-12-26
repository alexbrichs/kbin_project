from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from .user import User
from .thread import Publicacio

class Vot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publicacio = models.ForeignKey(Publicacio, on_delete=models.CASCADE)
    positiu = models.BooleanField()
    class Meta:
        unique_together = ('user', 'publicacio')



