from kbin.models import Publicacio, Thread, Link, Comment, User, Reply, Vote_comment
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from django.utils import timezone
from ..serializers.comment_serializer import CommentSerializer
from ..serializers.serializer_vots_comentaris import *

class VeureComentarisPublicacio(APIView):
    def get(self, request, id_publicacio, ordre):
        try:
            publicacio = Publicacio.objects.get(id=id_publicacio)
        except:
            return Response({"Error: No hi ha cap publicacio amb id {}".format(id_publicacio)}, status=404)

        comentaris = Comment.objects.filter(thread=publicacio, level=1)
        comentaris_serializer = CommentSerializer(comentaris, many=True).data

        if ordre == "top":
            comentaris_serializer = sorted(comentaris_serializer, key=lambda x: x['num_likes'], reverse=True)
        elif ordre == "newest":
            comentaris_serializer = sorted(comentaris_serializer, key=lambda x: x['creation_data'], reverse=True)
        elif ordre == "oldest":
            comentaris_serializer = sorted(comentaris_serializer, key=lambda x: x['creation_data'])
        else:
            return Response({"Error: No existeix l'ordre {}".format(ordre)}, status=404)

        return Response(comentaris_serializer)


class CrearComentari(APIView):
    def post(self, request, id_publicacio):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token de l'usuari"}, status=401)

        try:
            publicacio = Publicacio.objects.get(id=id_publicacio)
        except:
            return Response({"Error: No hi ha cap publicacio amb id {}".format(id_publicacio)}, status=404)

        body = request.data.get('body')
        if not body:
            return Response({"Error: Falta el body del comentari"}, status=400)

        try:
            usuari = User.objects.get(api_key=api_key)
        except:
            return Response({"Error: El token no correspon amb cap usuari registrat"}, status=403)

        comment = Comment.objects.create(author=usuari, thread=publicacio, body=body, level=1)
        comment.save()
        publicacio.num_coments += 1
        publicacio.save()

        comment = CommentSerializer(comment)
        return Response(comment.data, status=201)


class CrearComentariResposta(APIView):
    def post(self, request, id_comment):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token de l'usuari"}, status=401)

        try:
            comentari_root = Comment.objects.get(id=id_comment)
        except:
            return Response(
                {"Error": "No hi ha cap comentari amb id {}".format(id_comment)},
                status=404)

        body = request.data.get('body')
        if not body:
            return Response({"Error: Falta el body del comentari resposta"}, status=400)

        try:
            usuari = User.objects.get(api_key=api_key)
        except:
            return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

        publicacio = comentari_root.thread
        # Creem el comentari
        comment = Comment.objects.create(author=usuari, thread=comentari_root.thread, body=body,
                                         level=comentari_root.level + 1)
        comment.save()

        reply = Reply.objects.create(comment_root=comentari_root, comment_reply=comment)
        reply.save()

        comentari_root = CommentSerializer(comentari_root)

        publicacio.num_coments += 1
        publicacio.save()
        # Retorna el comentari origen perquè es vegi que s'ha creat la resposta
        return Response(comentari_root.data, status=201)

class ObtenirVotsComentaris(APIView):
    def get(self,request):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)
        try:
            usuari = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

        vots = Vote_comment.objects.filter(user_id=usuari.username)
        vots = VoteCommentSerializer(vots, many=True)
        print(vots)
        return Response(vots.data, status=200)


class VotarComentari(APIView):
    def post(self, request, id_comment, tipus_vot):
        validacio = self.validar_request(request, id_comment, tipus_vot)
        if isinstance(validacio, Response):
            return validacio
        usuari, comment = validacio

        if Vote_comment.objects.filter(user=usuari, comment=comment).exists():  # L'usuari ja ha votat
            vot = Vote_comment.objects.get(user=usuari, comment=comment)
            if tipus_vot == 'like':
                if vot.type == 'like':  # Si el vot ja era positiu no fem res i retornem la informació del Comentari
                    return retorna_info_comment(id_comment, status=200)

                else:  # Si el vot era negatiu canviem el sentit del vot
                    comment.num_dislikes -= 1
                    comment.num_likes += 1
                    vot.type = 'like'
                    vot.save()
                    comment.save()
                    return retorna_info_comment(id_comment, status=201)

            else:
                if vot.type == 'dislike':  # Si el vot ja era negatiu no fem res i retornem la informació del Comentari
                    return retorna_info_comment(id_comment, status=200)

                else:  # Si el vot era positiu canviem el sentit del vot
                    comment.num_dislikes += 1
                    comment.num_likes -= 1
                    vot.type = 'dislike'
                    vot.save()
                    comment.save()
                    return retorna_info_comment(id_comment, status=201)
        else:  # Creem un nou vot
            nou_vot = Vote_comment(user=usuari, comment=comment, type=tipus_vot)
            comment.num_likes += tipus_vot == "like"
            comment.num_dislikes += tipus_vot == "dislike"
            comment.save()
            nou_vot.save()
            return retorna_info_comment(id_comment, status=201)

    def delete(self, request, id_comment, tipus_vot):
        validacio = self.validar_request(request, id_comment, tipus_vot)
        if isinstance(validacio, Response):
            return validacio
        usuari, comment = validacio

        if Vote_comment.objects.filter(user=usuari, comment=comment).exists():  # L'usuari ha votat el comentari indicat
            vot = Vote_comment.objects.get(user=usuari, comment=comment)
            if (tipus_vot == 'like' and vot.type == 'like') or (tipus_vot == 'dislike' and vot.type == 'dislike'):
                vot.delete()
                comment.num_likes -= tipus_vot == 'like'
                comment.num_dislikes -= tipus_vot == 'dislike'
                comment.save()
                return Response({"Vot eliminat correctament"}, status=204)

            else:
                return Response({"El tipus de vot indicat i el del vot ja existent no coincideixen"}, status=400)

        else:  # L'usuari encara no ha votat
            return Response({"L'usuari indicat no ha votat el comentari amb ID {}".format(id_comment)}, status=404)

    def validar_request(self, request, id_comment, tipus_vot):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)

        if tipus_vot not in ["like", "dislike"]:
            return Response({"Error: El tipus de vot ha de ser like o dislike"}, status=400)

        try:
            usuari = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

        try:
            comment = Comment.objects.get(pk=id_comment)
        except Comment.DoesNotExist:
            return Response({"Error: no hi ha cap comentari amb ID {}".format(id_comment)}, status=404)

        return usuari, comment


class ComentariIndividual(APIView):
    def get(self, request, id_comment):
        try:
            comment = Comment.objects.get(pk=id_comment)
        except Comment.DoesNotExist:
            return Response({"Error: No hi ha cap comentari amb ID {}".format(id_comment)}, status=404)

        return retorna_info_comment(id_comment, status=200)

    def delete(self, request, id_comment):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)

        try:
            usuari = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

        try:
            comment = Comment.objects.get(pk=id_comment)
        except Comment.DoesNotExist:
            return Response({"Error: no hi ha cap comentari amb ID {}".format(id_comment)}, status=404)

        if comment.author_id != usuari.username:
            return Response({"Error: el token no correspon a l'usuari que ha creat la publicació"}, status=403)

        replies = Reply.objects.filter(comment_root=comment)
        thread = Publicacio.objects.get(pk=comment.thread_id)
        for reply in replies:
            reply_comment = reply.comment_reply
            reply_comment.delete()
            thread.num_coments -= 1
            thread.save()
        thread.num_coments -= 1
        thread.save()
        comment.delete()
        return Response({}, status=204)

    def put(self, request, id_comment):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)

        try:
            usuari = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

        try:
            comment = Comment.objects.get(pk=id_comment)
        except Comment.DoesNotExist:
            return Response({"Error: no hi ha cap comentari amb ID {}".format(id_comment)}, status=404)

        if comment.author_id != usuari.username:
            return Response({"Error: el token no correspon a l'usuari que ha creat la publicació"}, status=403)

        body = request.data.get('body')
        if not body:
            return Response({"Error: Falta el body del comentari"}, status=400)

        elif body == comment.body:
            return Response({"Error: El nou body ha de ser diferent de l'anterior"}, status=400)

        comment.body = body
        comment.last_edited = timezone.now()
        comment.save()
        return retorna_info_comment(id_comment, status=201)


def retorna_info_comment(id_comment, status):
    comment = Comment.objects.get(pk=id_comment)
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status)
