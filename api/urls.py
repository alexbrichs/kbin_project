from django.urls import path
from . import views

urlmagazines = [
    path('magazines/<str:ordre>/', views.LlistarMagazines.as_view(), name='llistar_magazines'),
    path('magazines/', views.CrearMagazine.as_view(), name='crear_magazine'),
    path('suscriptions/<int:magazine_id>/', views.CrearSuscripcio.as_view(), name='crear_suscripcio'),
    path('magazine/<int:magazine_id>/', views.VeureMagazine.as_view(), name='veure_magazine'),
    path('magazine/<int:magazine_id>/<str:filter>/<str:order>/', views.ObtenirPublicacionsMagazine.as_view(), name='obtenir_publicacions_magazines'),
    path('user_subscriptions/', views.ObtenirUserSubscriptions.as_view(), name='obtenir_user_subscriptions')
]

url_comentaris = [
    path('publicacions/<int:id_publicacio>/comments/<str:ordre>/', views.VeureComentarisPublicacio.as_view(),
         name='veure-comentaris-publicacio'),
    path('publicacions/<int:id_publicacio>/create_comment/', views.CrearComentari.as_view(), name='crear-comentari'),
    path('comments/create_reply/<int:id_comment>/', views.CrearComentariResposta.as_view(),
         name='crear-comentari-resposta'),
    path('comments/vote/<int:id_comment>/<str:tipus_vot>/', views.VotarComentari.as_view(), name='votar-comentari'),
    path('comments/<int:id_comment>/', views.ComentariIndividual.as_view(), name='obtenir-comentari'),
]

url_users = [
    path('users/', views.UserView.as_view(), {'username': None, 'element': 'threads', 'ordre': 'tot', 'filtre': 'newest'},  name='users'),
    path('u/<str:username>/', views.UserDetail.as_view(), name='user-info'),
    path('u/<str:username>/<str:element>/<str:ordre>/<str:filtre>/', views.UserView.as_view(), name='view-user'),
    path('settings/<str:username>/', views.UserView.as_view(), name='edit-user'),
    path('vots/',views.ObtenirVots.as_view(),name='obtenir-vots'),
    path('boosts/',views.ObtenirBoosts.as_view(),name='obtenir-boosts'),
    path('comments/vots/',views.ObtenirVotsComentaris.as_view(),name='obtenir-vots-comentaris'),
]

url_threads = [
    path('llistar/<str:filter>/<str:ordre>/', views.LlistaThreadLinks.as_view(), name='llistar_publicacions'),
    path('threads/',views.CrearThread.as_view(), name='crear_thread'),
    path('links/',views.CrearLink.as_view(),name='crear_link'),
    path('publicacions/votar/<int:id_publicacio>/<str:tipus_vot>/',views.VotarPublicacio.as_view(),name='votar_publicacio'),
    path('cercador/<str:filter>/<str:ordre>/',views.CercarPublicacions.as_view(),name='cercador'),
    path('publicacions/<int:id_publicacio>/',views.PublicacioIndividual.as_view(),name='obtenir_publicacio'),
    path('publicacions/boost/<int:id_publicacio>/',views.ImpulsarPublicacio.as_view(),name='obtenir_publicacio')
]

urlpatterns = [

] + urlmagazines + url_users + url_comentaris + url_threads
