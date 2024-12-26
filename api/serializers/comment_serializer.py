from rest_framework import serializers
from kbin.models import Comment, Thread, Link, Reply


class CommentSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        # TODO: Cal posar el level?
        # Field 'parent' necessari per quan es mostren els comentaris d'un user
        fields = ['id', 'author', 'body', 'creation_data', 'last_edited', 'num_likes', 'num_dislikes',
                  'level', 'parent', 'replies']

    def get_parent(self, obj):
        base = "http://127.0.0.1:8000/api/"
        if Thread.objects.filter(id=obj.thread_id).exists():
            base += "threads/" + str(obj.thread_id) + "/"
        elif Link.objects.filter(id=obj.thread_id).exists():
            base += "links/" + str(obj.thread_id) + "/"

        return base

    def get_replies(self, obj):
        replies = Reply.objects.filter(comment_root=obj)
        reply_comments = [reply.comment_reply for reply in replies]
        return CommentSerializer(reply_comments, many=True).data
