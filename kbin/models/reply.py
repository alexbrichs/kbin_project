from django.db import models
from . import Comment


class Reply(models.Model):
    comment_root = models.ForeignKey(Comment, related_name='root_comments', on_delete=models.CASCADE)
    comment_reply = models.ForeignKey(Comment, related_name='reply_comments', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('comment_root', 'comment_reply'),)
