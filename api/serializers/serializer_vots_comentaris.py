from rest_framework import serializers
from kbin.models.vote_comment import *

class VoteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote_comment
        fields = ['comment_id','type']
