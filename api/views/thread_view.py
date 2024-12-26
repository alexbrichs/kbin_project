from django.db.models import Q
from kbin.models import Publicacio, Thread, Link, Vot, Boost
from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers.serializer_threads import *
from ..serializers.serializer_vots import *
from ..serializers.serializer_boosts import *
import json


class LlistaThreadLinks(APIView):
    def get(self, request, filter, ordre):
        # Obtenim publicacions segons filtre:
        links = Link.objects.all()
        threads = Thread.objects.all()

        return filtrar_ordenar(threads, links, filter, ordre)


class CrearThread(APIView):
    def post(self, request):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)
        data = request.data
        required_fields = {"title", "magazine", "body"}
        if required_fields.issubset(data.keys()):
            if len(data["title"]) == 0:
                return Response({"error: Titol buit"}, status=400)

            try:  #Comprovem si el magazine indicat existeix
                magazine = Magazine.objects.get(pk=data["magazine"])
            except:
                return Response({"Error: No hi ha un magazine amb ID {}".format(data["magazine"])}, status=400)

            try:
                usuari = User.objects.get(api_key=api_key)
            except:
                return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

            nou_thread = Thread.objects.create(author=usuari, title=data["title"], body=data["body"], magazine=magazine)
            nou_thread = ThreadSerializer(nou_thread)
            return Response(nou_thread.data, status=201)  # 201: Created
        else:
            #Falta algun dels camps
            return Response(
                {"Error: Falten atributs. Cal indicar titol, body i la ID del magazine del thread a crear."},
                status=400)


class CrearLink(APIView):
    def post(self, request):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)

        data = request.data
        required_fields = {"title", "magazine", "url", "body"}
        if required_fields.issubset(data.keys()):
            if len(data["title"]) == 0:
                return Response({"Error: Titol buit"}, status=400)

            if len(data["url"]) == 0:
                return Response({"Error: URL no indicada"}, status=400)

            try:  #Comprovem si el magazine indicat existeix
                magazine = Magazine.objects.get(pk=data["magazine"])
            except:
                return Response({"Error: No hi ha un magazine amb ID {}".format(data["magazine"])}, status=400)

            try:
                usuari = User.objects.get(api_key=api_key)
            except:
                return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

            nou_link = Link.objects.create(author=usuari, title=data["title"], body=data["body"],
                                           magazine=magazine, url=data["url"])

            nou_link = LinkSerializer(nou_link)
            return Response(nou_link.data, status=201)  # 201: Created
        else:
            # Si los campos no coinciden, retornamos un error
            return Response({"Error: Falten atributs. Cal indicar titol, body, magazine i url del link a crear."},
                            status=400)  # 400: Bad Request


class ObtenirBoosts(APIView):
    def get(self, request):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)
        try:
            usuari = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

        boosts = Boost.objects.filter(user_id=usuari.username)
        boosts = BoostSerializer(boosts, many=True)
        return Response(boosts.data, status=200)


class ObtenirVots(APIView):
    def get(self, request):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)
        try:
            usuari = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

        vots = Vot.objects.filter(user_id=usuari.username)
        vots = VotSerializer(vots, many=True)
        return Response(vots.data, status=200)


class VotarPublicacio(APIView):
    def post(self, request, id_publicacio, tipus_vot):
        validacio = validar_request(request, id_publicacio)
        if isinstance(validacio, Response):
            return validacio
        usuari, publicacio = validacio

        if tipus_vot not in ["like", "dislike"]:
            return Response({"Error: El tipus de vot ha de ser like o dislike"}, status=400)

        if Vot.objects.filter(user=usuari, publicacio=publicacio).exists():  #L'usuari ja ha votat
            vot = Vot.objects.get(user=usuari, publicacio=publicacio)
            if tipus_vot == 'like':
                if vot.positiu:  # Si el vot ja era positiu no fem res i retornem la informació del Thread o el Link
                    return retorna_info_publicacio(id_publicacio, 200)

                else:  #Si el vot era negatiu canviem el sentit del vot
                    publicacio.num_dislikes -= 1
                    publicacio.num_likes += 1
                    vot.positiu = True
                    vot.save()
                    publicacio.save()
                    return retorna_info_publicacio(id_publicacio, 200)

            else:
                if not vot.positiu:  # Si el vot ja era negatiu no fem res i retornem la informació del Thread o el Link
                    return retorna_info_publicacio(id_publicacio, 200)

                else:  #Si el vot era positiu canviem el sentit del vot
                    publicacio.num_dislikes += 1
                    publicacio.num_likes -= 1
                    vot.positiu = False
                    vot.save()
                    publicacio.save()
                    return retorna_info_publicacio(id_publicacio, 200)
        else:  #Creem un nou vot
            nou_vot = Vot(user=usuari, publicacio=publicacio, positiu=tipus_vot == "like")
            publicacio.num_likes += tipus_vot == "like"
            publicacio.num_dislikes += tipus_vot == "dislike"
            publicacio.save()
            nou_vot.save()
            return retorna_info_publicacio(id_publicacio, 201)

    def delete(self, request, id_publicacio, tipus_vot):
        validacio = validar_request(request, id_publicacio)
        if isinstance(validacio, Response):
            return validacio
        usuari, publicacio = validacio

        if tipus_vot not in ["like", "dislike"]:
            return Response({"Error: El tipus de vot ha de ser like o dislike"}, status=400)

        if Vot.objects.filter(user=usuari, publicacio=publicacio).exists():  # L'usuari ha votat la publicacio indicada
            vot = Vot.objects.get(user=usuari, publicacio=publicacio)
            if ((tipus_vot == 'like' and vot.positiu) or (tipus_vot == 'dislike' and not vot.positiu)):
                vot.delete()
                publicacio.num_likes -= tipus_vot == 'like'
                publicacio.num_dislikes -= tipus_vot == 'dislike'
                publicacio.save()
                return Response({}, status=204)

            else:
                return Response({"El tipus de vot indicat i el del vot ja existent no coincideixen"}, status=400)

        else:  #L'usuari encara no ha votat
            return Response({"L'usuari indicat no ha votat la publicació amb ID {}".format(id_publicacio)}, status=404)


class CercarPublicacions(APIView):
    def get(self, request, filter, ordre):
        keyword = request.headers.get('keyword')

        if all(char.isspace() for char in keyword):  #Només s'han introduït espais en blanc
            return Response({"La keyword de la cerca no pot ser només espais en blanc"}, status=400)

        # Busquem totes les publicacions que contenen en el titol i el cos la keyword indicada
        links = Link.objects.filter(Q(title__contains=keyword) | Q(body__contains=keyword))
        threads = Thread.objects.filter(Q(title__contains=keyword) | Q(body__contains=keyword))

        return filtrar_ordenar(threads, links, filter, ordre)


class PublicacioIndividual(APIView):
    def get(self, request, id_publicacio):
        if Publicacio.objects.filter(pk=id_publicacio).exists():
            return retorna_info_publicacio(id_publicacio, 200)
        else:
            return Response({"Error: No existeix una publicació amb ID {}".format(id_publicacio)}, status=404)

    def delete(self, request, id_publicacio):
        validacio = validar_request(request, id_publicacio)
        if isinstance(validacio, Response):
            return validacio
        usuari, publicacio = validacio

        if publicacio.author_id != usuari.username:
            return Response({"Error: el token no correspon a l'usuari que ha creat la publicació"}, status=403)

        publicacio.delete()
        return Response({}, status=204)

    def put(self, request, id_publicacio):
        validacio = validar_request(request, id_publicacio)
        if isinstance(validacio, Response):
            return validacio
        usuari, publicacio = validacio

        if publicacio.author_id != usuari.username:
            return Response({"Error: el token no correspon a l'usuari que ha creat la publicació"}, status=403)

        data = request.data

        if "title" in data.keys():
            if len(data["title"]) == 0:
                return Response({"Error: El titol de la publicació no pot ser buit."}, status=400)
            else:
                publicacio.title = data["title"]

        if "body" in data.keys():
            publicacio.body = data["body"]
        publicacio.save()
        return retorna_info_publicacio(id_publicacio, 200)


class ImpulsarPublicacio(APIView):
    def post(self, request, id_publicacio):
        validacio = validar_request(request, id_publicacio)
        if isinstance(validacio, Response):
            return validacio
        usuari, publicacio = validacio
        num_status = 200
        if not Boost.objects.filter(user=usuari,
                                    publicacio_id=id_publicacio).exists():  #L'usuari encara no ha fet boost de la publicació
            nou_boost = Boost(user=usuari, publicacio_id=id_publicacio)
            publicacio.num_boosts += 1
            publicacio.save()
            nou_boost.save()
            num_status = 201
        return retorna_info_publicacio(id_publicacio, num_status)

    def delete(self, request, id_publicacio):
        validacio = validar_request(request, id_publicacio)
        if isinstance(validacio, Response):
            return validacio
        usuari, publicacio = validacio

        if Boost.objects.filter(user=usuari,
                                publicacio_id=id_publicacio).exists():  #L'usuari ha fet boost de la publicació
            publicacio.num_boosts -= 1
            publicacio.save()
            boost = Boost.objects.get(user=usuari, publicacio=publicacio)
            boost.delete()
            return Response({}, status=204)

        else:
            return Response({"L'usuari indicat no ha impulsat la publicació amb ID {}".format(id_publicacio)},
                            status=404)


def retorna_info_publicacio(IDPublicacio, num_status):
    try:
        thread = Thread.objects.get(pk=IDPublicacio)
        thread = ThreadSerializer(thread)
        return Response(thread.data, status=num_status)
    except:
        link = Link.objects.get(pk=IDPublicacio)
        link = LinkSerializer(link)
        return Response(link.data, status=num_status)


def filtrar_ordenar(threads, links, filter, ordre):
    thread_serializer = ThreadSerializer(threads, many=True)
    link_serializer = LinkSerializer(links, many=True)

    if filter == 'links':
        resultats_serializer = link_serializer.data
    elif filter == 'threads':
        resultats_serializer = thread_serializer.data
    elif filter == 'publicacions':
        resultats_serializer = thread_serializer.data + link_serializer.data
    else:
        return Response({"Error: No existeix el filtre {}".format(filter)}, status=404)

    if ordre == 'newest':
        tot = sorted(resultats_serializer, key=lambda x: x['creation_data'], reverse=True)
    elif ordre == 'commented':
        tot = sorted(resultats_serializer, key=lambda x: x['num_coments'], reverse=True)
    elif (ordre == 'top'):
        tot = sorted(resultats_serializer, key=lambda x: x['num_likes'], reverse=True)
    else:
        return Response({"Error: No existeix l'ordre {}".format(ordre)}, status=404)

    return Response(tot)


def validar_request(request, id_publicacio):
    api_key = request.headers.get('Authorization')
    if api_key is None:
        return Response({"Error: Es necessari indicar el token del usuari"}, status=401)
    try:
        usuari = User.objects.get(api_key=api_key)
    except User.DoesNotExist:
        return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

    try:
        publicacio = Publicacio.objects.get(pk=id_publicacio)
    except Publicacio.DoesNotExist:
        return Response({"Error: no hi ha cap publicació amb ID {}".format(id_publicacio)}, status=404)

    return usuari, publicacio
