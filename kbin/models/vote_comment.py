from django.db import models
from . import Comment, User


class Vote_comment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.TextField(default='like')  # like or dislike, no deixa sense default?

    class Meta:
        unique_together = (('comment', 'user'),)
