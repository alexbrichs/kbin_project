from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse,reverse_lazy
from itertools import chain
from django.db.models import Value, CharField
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from ..models import *
import secrets

@csrf_exempt
def sort(all, ordre):
    if ordre == 'top':
        res = sorted(all, key=lambda x: x.num_likes, reverse=True)
    elif ordre == 'newest':
        res = sorted(all, key=lambda x: x.creation_data, reverse=True)
    elif ordre == 'commented':
        res = sorted(all, key=lambda x: x.num_coments, reverse=True)
    return res

def view_user(request, username, filter=None,ordre=None,select='threads'):
    template = loader.get_template('view_user.html')
    obj = User.objects.get(username=username)
    links_tot = Link.objects.filter(author_id=username)
    threads_tot = Thread.objects.filter(author_id=username)
    comments = Comment.objects.filter(author_id=username)
    boosts = Boost.objects.filter(user_id=username)

    nboosts =len(boosts)
    nthreads = len(list(links_tot)+list(threads_tot))
    ncom = len(comments)
    if select == 'threads':

        context = {'usuari2': obj, 'threads': ordena(links_tot,threads_tot,ordre,filter),
                   'active_option': ordre, 'active_filter': filter, 'selected': select,
                   'n_threads' : nthreads,'n_com' : ncom,'n_boosts' : nboosts}

    elif select == 'com':
        if ordre == 'top':
            comments = sorted(comments, key=lambda x: x.num_likes, reverse=True)
        elif ordre == 'newest':
            comments = sorted(comments, key=lambda x: x.creation_data, reverse=True)
        else:
            comments = sorted(comments, key=lambda x: x.creation_data, reverse=False)
        thread_ids = [comment.thread_id for comment in comments]

        links = []
        threads = []
        # Itera pels IDs i afegix manualment les instàncies corresponents a les llistes
        for thread_id in thread_ids:
            # Afegeix els links corresponents a la llista de links
            links.extend(Link.objects.filter(id=thread_id))
            # Afegeix els threads corresponents a la llista de threads
            threads.extend(Thread.objects.filter(id=thread_id))


        publicacions = sorted(chain(links, threads), key=lambda x: thread_ids.index(x.id))
        parella = [(commen, publicacion) for commen, publicacion in
                                          zip(comments, publicacions)]


        context = {'usuari2': obj, 'coments': comments, 'active_option': ordre, 'active_filter': filter,
                   'selected': select,'pare':parella,'n_threads' : nthreads,'n_com' : ncom,'n_boosts' : nboosts}

    else:

        publication_ids = boosts.values_list('publicacio_id', flat=True)

        links = Link.objects.filter(id__in=publication_ids)
        threads = Thread.objects.filter(id__in=publication_ids)

        context = {'usuari2': obj, 'threads': ordena(links,threads,ordre,filter), 'active_option': ordre,
                   'active_filter': filter, 'selected': select,'n_threads' : nthreads,'n_com' : ncom,'n_boosts' : nboosts}

    return HttpResponse(template.render(context, request))


def ordena(links,threads,ordre,filter):
    if filter == 'links':
        tot = links
    elif filter == 'threads':
        tot = threads
    else:
        tot = list(links) + list(threads)

    if ordre == 'top':
        tot = sorted(tot, key=lambda x: x.num_likes, reverse=True)
    elif ordre == 'newest':
        tot = sorted(tot, key=lambda x: x.creation_data, reverse=True)
    elif ordre == 'commented':
        tot = sorted(tot, key=lambda x: x.num_coments, reverse=True)
    return tot
  

@csrf_exempt
def get_username(user_email):
    return user_email.split('@')[0]


@csrf_exempt
def login(request):
    user_email = request.user.email
    djando_username = request.user.username
    user_username = get_username(user_email)
    if not User.objects.filter(username=user_username).exists():
        User.objects.create(
            username=user_username,
            email=user_email,
            api_key=secrets.token_hex(20)
        )
    if request.user.is_authenticated:
        url = reverse('main') + f'?django_user={djando_username}&user={user_username}'
        return redirect(url)


@csrf_exempt
def edit_user(request, username):
    if request.method == "POST":
        obj = User.objects.get(username=username)
        description = request.POST.get('description')
        if description is not None:
            obj.description = description
        avatar = request.FILES.get('avatar')
        if avatar is not None:
            avatar_name = default_storage.save('avatar/' + avatar.name, avatar)
            obj.avatar = default_storage.url(avatar_name)
        cover = request.FILES.get('cover')
        if cover is not None:
            cover_name = default_storage.save('cover/' + cover.name, cover)
            obj.cover = default_storage.url(cover_name)
        obj.save()
        template = loader.get_template('edit_user.html')
        context = {'usuari2': obj}
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('edit_user.html')
        obj = User.objects.get(username=username)
        context = {'usuari2': obj}
        return HttpResponse(template.render(context, request))


@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect("/")


