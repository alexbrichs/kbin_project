from rest_framework import serializers
from kbin.models.magazine import *

class MagazineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magazine
        fields = ['id', 'author', 'creation_date', 'name', 'title', 'description', 'rules',
                  'nsfw', 'total_threads', 'total_links', 'total_publicacions', 'total_comments', 'n_suscriptions']

