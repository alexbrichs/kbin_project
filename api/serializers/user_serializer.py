from rest_framework import serializers
from kbin.models.user import User


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    total_threads = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    total_boosts = serializers.SerializerMethodField()
    avatar = serializers.URLField()
    cover = serializers.URLField()

    class Meta:
        model = User
        fields = ['username', 'description', 'token', 'cover', 'avatar', 'email',
                  'total_threads', 'total_comments', 'total_boosts']

    def get_token(self, obj):
        if obj.api_key == self.context.get('api_key'):
            return obj.api_key
        return None

    def get_total_threads(self, obj):
        return obj.total_threads

    def get_total_comments(self, obj):
        return obj.total_comments

    def get_total_boosts(self, obj):
        return obj.total_boosts

