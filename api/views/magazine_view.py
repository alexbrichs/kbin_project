from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers.serializer_magazines import *
from ..serializers.subscription_serializer import *
from ..serializers.link_serializer import *
from ..serializers.thread_serializer import *


class LlistarMagazines(APIView):
    def get(self, request, ordre):
        magazines = Magazine.objects.all()
        if ordre == 'threads':
            magazine_threads = {}
            for magazine in magazines:
                magazine_threads[magazine.id] = magazine.total_threads()

            magazines = sorted(magazines, key=lambda x: magazine_threads.get(x.id, 0), reverse=True)
            magazines_serializer = MagazineSerializer(magazines, many=True).data

        elif ordre == 'elements':
            magazine_elements = {}
            for magazine in magazines:
                magazine_elements[magazine.id] = magazine.total_publicacions()

            magazines = sorted(magazines, key=lambda x: magazine_elements.get(x.id, 0), reverse=True)
            magazines_serializer = MagazineSerializer(magazines, many=True).data

        elif ordre == 'commented':
            magazine_comments = {}
            for magazine in magazines:
                magazine_comments[magazine.id] = magazine.total_comments()
            magazines = sorted(magazines, key=lambda x: magazine_comments.get(x.id, 0), reverse=True)
            magazines_serializer = MagazineSerializer(magazines, many=True).data

        elif ordre == 'suscriptions':
            magazines_serializer = MagazineSerializer(magazines, many=True).data
            magazines_serializer = sorted(magazines_serializer, key=lambda x: x['n_suscriptions'], reverse=True)

        else:
            return Response({"Error: La url sol·licitada no existeix"}, status=404)
        return Response(magazines_serializer, status=200)


class CrearMagazine(APIView):
    def post(self, request):
        api_key = request.headers.get('Authorization')
        if (api_key == None):
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)
        data = request.data
        required_fields = {"name", "title"}
        if required_fields.issubset(data.keys()):
            if len(data["name"]) == 0:
                return Response({"error: Nom buit"}, status=400)
            elif len(data["title"]) == 0:
                return Response({"error: Títol buit"}, status=400)
            try:
                usuari = User.objects.get(api_key=api_key)
            except:
                return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)

            description = data.get("description")
            rules = data.get("rules")
            nsfw = data.get("nsfw")
            test_magazine = Magazine.objects.filter(name=data["name"]).exists()
            if (test_magazine):
                return Response({"Error: ja existeix una magazine amb el nom introduït"}, status=409)

            nou_magazine = Magazine.objects.create(author=usuari,
                                                   name=data["name"],
                                                   creation_date=timezone.now().isoformat(),
                                                   title=data["title"],
                                                   description=description,
                                                   rules=rules,
                                                   nsfw=nsfw)

            nou_magazine = MagazineSerializer(nou_magazine)
            return Response(nou_magazine.data, status=201)
        else:
            return Response({"Error: Falten atributs. Cal indicar nom i títol de la magazine a crear."},
                            status=400)


class CrearSuscripcio(APIView):
    def post(self, request, magazine_id):

        api_key = request.headers.get('Authorization')
        if (api_key == None):
            return Response({"Error: Es necessari indicar el token del usuari"}, status=401)
        try:
            usuari = User.objects.get(api_key=api_key)
        except:
            return Response({"Error: el token no correspon amb cap usuari registrat"}, status=403)
        try:
            magazine = Magazine.objects.get(pk=magazine_id)
        except:
            return Response({"Error: La magazine sol·licitada no s'ha trobat"}, status=404)

        suscripcio = Subscription.objects.filter(user=usuari, magazine=magazine)
        if suscripcio.exists():
            return Response({"Error: L'usuari loguejat ja esta subscrit a la magazine indicada."}, status=400)
        else:
            nou_suscripcio = Subscription.objects.create(user=usuari, magazine=magazine)
            nou_suscripcio.save()
            nou_suscripcio = SubscriptionSerializer(nou_suscripcio)
            magazine.n_suscriptions += 1
            magazine.save()
            return Response(nou_suscripcio.data, status=201)

    def delete(self, request, magazine_id):
        api_key = request.headers.get('Authorization')
        if (api_key == None):
            return Response({"Error: No s'ha indicat el token de l'usuari"}, status=401)
        try:
            usuari = User.objects.get(api_key=api_key)
        except:
            return Response({"Error: El token indicat no és vàlid"}, status=403)
        try:
            magazine = Magazine.objects.get(pk=magazine_id)
        except:
            return Response({"Error: El magazine sol·licitat no s'ha trobat"}, status=404)

        suscripcio = Subscription.objects.filter(user=usuari, magazine=magazine)
        if suscripcio.exists():
            Subscription.objects.filter(user=usuari, magazine=magazine).delete()
            magazine.n_suscriptions -= 1
            magazine.save()
            return Response(status=204)
        else:
            return Response({"Error: L'usuari loguejat no està subscrit a la magazine indicada."}, status=400)


class VeureMagazine(APIView):
    def get(self, request, magazine_id):
        try:
            magazine = Magazine.objects.get(pk=magazine_id)
        except:
            return Response({"Error: El magazine sol·licitat no s'ha trobat"}, status=404)
        magazine = MagazineSerializer(magazine)
        return Response(magazine.data, status=200)


class ObtenirPublicacionsMagazine(APIView):
    def get(self, request, magazine_id, filter, order):
        try:
            magazine = Magazine.objects.get(pk=magazine_id)
        except:
            return Response({"Error: El magazine sol·licitat no s'ha trobat"}, status=404)

        links = Link.objects.filter(magazine_id=magazine_id)
        threads = Thread.objects.filter(magazine_id=magazine_id)
        return filtrar_ordenar(threads, links, filter, order)


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

    return Response(tot, status=200)


class ObtenirUserSubscriptions(APIView):
    def get(self, request):
        api_key = request.headers.get('Authorization')
        if api_key is None:
            return Response({"Error": "No s'ha indicat el token de l'usuari"}, status=401)

        try:
            usuari = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            return Response({"Error": "El token indicat no és vàlid"}, status=403)


        suscripcions = Subscription.objects.filter(user=usuari)

        serialized_suscripcions = SubscriptionSerializer(suscripcions, many=True).data

        return Response(serialized_suscripcions, status=200)

