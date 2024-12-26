from rest_framework import serializers
from kbin.models.subscription import *

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'magazine']
        unique_together = ('user', 'magazine')

