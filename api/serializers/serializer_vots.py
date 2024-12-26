from rest_framework import serializers
from kbin.models.votes import *

class VotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vot
        fields = ['publicacio_id','positiu']
