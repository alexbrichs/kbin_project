from rest_framework import serializers
from kbin.models.boost import *


class BoostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boost
        fields = ['publicacio_id']
