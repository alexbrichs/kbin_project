from rest_framework import serializers
from kbin.models.thread import *


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'
