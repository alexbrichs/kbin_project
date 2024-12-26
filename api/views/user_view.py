from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage

from ..serializers.user_serializer import UserSerializer
from ..serializers.thread_serializer import ThreadSerializer
from ..serializers.serializer_threads import LinkSerializer
from ..serializers.comment_serializer import CommentSerializer
from kbin.models import User, Thread, Link, Comment, Boost


class UserView(APIView):
    def get(self, request, username, element, ordre, filtre):
        if username:
            return self.retrieve(request, username, element, ordre, filtre)
        else:
            return self.list(request)

    def put(self, request, username):
        api_key = request.headers.get('Authorization')
        data = request.data
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": f"The user '{username}' does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        if api_key is None:
            return Response({"error: The API key is missing"},
                            status=status.HTTP_401_UNAUTHORIZED)
        if user != User.objects.get(api_key=api_key):
            return Response({"error": f"the token provided does not match the user"},
                            status=status.HTTP_400_BAD_REQUEST)

        user.description = data['description']
        avatar = request.FILES.get('avatar')
        if avatar is not None:
            avatar_name = default_storage.save('avatar/' + avatar.name, avatar)
            user.avatar = default_storage.url(avatar_name)
        cover = request.FILES.get('cover')
        if cover is not None:
            cover_name = default_storage.save('cover/' + cover.name, cover)
            user.cover = default_storage.url(cover_name)
        user.save()
        user_updated_serializer = UserSerializer(user, context={'api_key': api_key})
        return Response(user_updated_serializer.data, status=201)  # 201: Created

    def retrieve(self, request, username, element, ordre, filtre):
        result = None
        try:
            api_key = request.headers.get('Authorization')
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": f"The user '{username}' does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        user_serializer = UserSerializer(user, context={'api_key': api_key})
        if filtre is None:
            filtre = 'tot'
        if element is None:
            element = 'threads'

        if element == 'threads':
            tot_ordenat = filtrar(filtre, username, ordre, False)
            result = tot_ordenat

        elif element == 'comments':
            comments = Comment.objects.filter(author=username)
            # Son tots els comentaris
            if filtre == 'tot':
                pass
            elif filtre == 'threads':
                comment_thread = []
                for comment in comments:
                    if Thread.objects.filter(id=comment.thread_id).exists():
                        comment_thread.append(comment)
                comments = comment_thread
            elif filtre == 'links':
                comment_link = []
                for comment in comments:
                    if Link.objects.filter(id=comment.thread_id).exists():
                        comment_link.append(comment)
                comments = comment_link
            else:
                return Response({"error": f"The filter '{filtre}' does not exist"},
                                status=status.HTTP_404_NOT_FOUND)

            comment_serializer = CommentSerializer(comments, many=True)
            tot_ordenat = get_ordena(comment_serializer.data, ordre)
            for comment in tot_ordenat:
                comment.pop("replies", None)
            result = tot_ordenat
        elif element == 'boosts':
            if api_key is None:
                return Response({"Error: Es necessari indicar el token del usuari"}, status=401)
            try:
                user_token = User.objects.get(api_key=api_key)
            except User.DoesNotExist:
                return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

            if user != user_token:
                return Response({"Error: el token no correspon a l'usuari"}, status=403)
            elif user == User.objects.get(api_key=api_key):
                tot_ordenat = filtrar(filtre, username, ordre, True)
                result = tot_ordenat
        else:
            return Response({"error": f"The element '{element}' does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = {
            "user": user_serializer.data,
            "data": result
        }
        return Response(serializer, status=status.HTTP_200_OK)

    def list(self, request):
        users = User.objects.all()
        serializers = UserSerializer(users, many=True, context={'api_key': None})
        for serializer in serializers.data:
            user = User.objects.get(username=serializer['username'])
            serializer['token'] = user.api_key
        return Response(serializers.data, status=status.HTTP_200_OK)


class UserDetail(APIView):
    def get(self, request, username):
        api_key = request.headers.get('Authorization')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": f"The user '{username}' does not exist"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, context={'api_key': api_key})
        return Response(serializer.data, status=status.HTTP_200_OK)


def filtrar(filtre, username, ordre, boost):
    if filtre == 'tot':
        thread_serializer = get_thread_serialized(username, boost)
        link_serializer = get_link_serialized(username, boost)
        tot = link_serializer.data + thread_serializer.data
        tot_ordenat = get_ordena(tot, ordre)
    elif filtre == 'threads':
        thread_serializer = get_thread_serialized(username, boost)
        tot_ordenat = get_ordena(thread_serializer.data, ordre)
    elif filtre == 'links':
        link_serializer = get_link_serialized(username, boost)
        tot_ordenat = get_ordena(link_serializer.data, ordre)
    else:
        return Response({"error": f"The filter '{filtre}' does not exist"},
                        status=status.HTTP_404_NOT_FOUND)
    return tot_ordenat


def get_thread_serialized(username, boost):
    if boost:
        boosts = Boost.objects.filter(user=username)
        publication_ids = boosts.values_list('publicacio_id', flat=True)
        threads = Thread.objects.filter(id__in=publication_ids)
    else:
        threads = Thread.objects.filter(author=username)
    thread_serializer = ThreadSerializer(threads, many=True)
    return thread_serializer


def get_link_serialized(username, boost):
    if boost:
        boosts = Boost.objects.filter(user=username)
        publication_ids = boosts.values_list('publicacio_id', flat=True)
        links = Link.objects.filter(id__in=publication_ids)
    else:
        links = Link.objects.filter(author=username)
    link_serializer = LinkSerializer(links, many=True)
    return link_serializer


def get_ordena(elements, ordre):
    try:
        tot_ordenat = ordena(elements, ordre)
        return tot_ordenat
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


def ordena(elements, ordre):
    if ordre is None or ordre == 'newest':
        elements = sorted(elements, key=lambda x: x['creation_data'], reverse=True)
    elif ordre == 'top':
        elements = sorted(elements, key=lambda x: x['num_likes'], reverse=True)
    elif ordre == 'commented':
        elements = sorted(elements, key=lambda x: x['num_coments'], reverse=True)
    elif ordre == 'oldest':
        elements = sorted(elements, key=lambda x: x['creation_data'])
    else:
        raise Exception(f"The order '{ordre}' does not exist")
    return elements
