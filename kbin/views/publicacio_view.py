from django.http import JsonResponse
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, redirect
from ..models import *
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.decorators import login_required


@login_required(redirect_field_name='login')
@csrf_exempt
def boost_publicacio(request, thread_id):
    publicacio = Publicacio.objects.get(pk=thread_id)
    user = User.objects.get(email=request.user.email)

    if request.method == 'POST':

        # Mirem si l'usuari ja ha fet boost vol dir que l'hem de treure
        if Boost.objects.filter(user=user, publicacio=publicacio).exists():
            boost = Boost.objects.get(user=user, publicacio=publicacio)
            publicacio.num_boosts -= 1
            publicacio.save()
            boost.delete()

        else:  # Usuari encara no ha fet boost
            nou_boost = Boost(user=user, publicacio=publicacio)
            publicacio.num_boosts += 1
            publicacio.save()
            nou_boost.save()

    return redirect('main')


@csrf_exempt
def editar_thread(request, thread_id):
    thread = Thread.objects.get(pk=thread_id)
    if request.method == "POST":
        thread.title = request.POST.get('title')
        thread.body = request.POST.get('body')
        thread.save()
        return veure_thread(request, thread_id, 'top', True)
    else:
        template = loader.get_template('edit_publicacio.html')
        return HttpResponse(template.render({'thread': thread, 'titol': thread.title, 'body': thread.body,
                                             'magazine': thread.magazine.name}, request))


@csrf_exempt
def editar_link(request, thread_id):
    link = Link.objects.get(pk=thread_id)
    if request.method == "POST":
        link.title = request.POST.get('title')
        link.body = request.POST.get('body')
        link.save()
        return veure_thread(request, thread_id, 'top', True)
    else:
        template = loader.get_template('edit_publicacio.html')
        return HttpResponse(template.render({'thread': link, 'titol': link.title, 'body': link.body, 'url': link.url,
                                             'magazine': link.magazine.name}, request))


@csrf_exempt
def eliminar_publicacio(request, thread_id):
    thread = Publicacio.objects.get(pk=thread_id)
    if request.method == "POST":
        thread.delete()
    template = loader.get_template('home.html')
    return main_list(request, eliminat=True)


def main_list(request, ordre=None, filter=None, eliminat=None):
    links = Link.objects.all()
    threads = Thread.objects.all()
    user = request.GET.get('user')
    django_username = request.GET.get('django_user')
    djangoUser = {}
    if user is not None and django_username is not None:
        djangoUser = {
            'user': DjangoUser.objects.get(username=django_username),
            'username': user,
        }

    if ordre == '': ordre = 'newest'

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

    context = {'threads': tot, 'active_option': ordre, 'active_filter': filter, 'eliminat': eliminat}
    template = loader.get_template('home.html')
    return HttpResponse(template.render(context, request))


@login_required(redirect_field_name='login')
def new_link(request):
    magazines = Magazine.objects.all()
    context = {'magazines': magazines}
    template = loader.get_template('new_link.html')
    return HttpResponse(template.render(context, request))


@login_required(redirect_field_name='login')
def new_thread(request):
    magazines = Magazine.objects.all()
    context = {'magazines': magazines}
    template = loader.get_template('new_thread.html')
    return HttpResponse(template.render(context, request))


@csrf_exempt
def create_link_thread(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        url = request.POST.get('url')
        magazine = Magazine.objects.get(id=request.POST.get('magazine'))
        created_at = timezone.now().isoformat()
        author_email = request.user.email
        user = User.objects.get(email=author_email)
        if body == '':
            body = None

        author_email = request.user.email
        user = User.objects.get(email=author_email)

        # Creem una nova instància del model Thread o Link amb les dades proporcionades
        if url == None:
            thread = Thread.objects.create(
                title=title,
                body=body,
                author=user,
                magazine=magazine,
                creation_data=created_at,
            )
        else:
            if url.startswith("https://"):
                url = url[len("https://"):]
            elif url.startswith("http://"):
                url = url[len("http://"):]

            if not url.startswith("www."):
                url = f"www.{url}"
            url = url.strip('/')
            link = Link.objects.create(
                title=title,
                body=body,
                url=url,
                author=user,
                magazine=magazine,
                creation_data=created_at
            )

        # Un cop s'ha creat el fil de discussió, redirigeix l'usuari a alguna altra pàgina
        return redirect('main')
    else:
        # Si la petició no és POST, simplement mostrem el formulari
        return redirect('/new')


@login_required(redirect_field_name='login')
@csrf_exempt
def boost_thread(request, thread_id):
    if request.method == 'POST':
        thread = Publicacio.objects.get(pk=thread_id)
        thread.num_boosts += 1
        thread.save()
        next = url_redireccio(request)
        return HttpResponseRedirect(next)

    else:
        return redirect('main')


def veure_thread(request, thread_id, order, edited=False):
    if Thread.objects.filter(pk=thread_id).exists():
        thread = Publicacio.objects.get(pk=thread_id)
    else:
        thread = Link.objects.get(pk=thread_id)

    if order == 'newest':
        comments_root = Comment.objects.filter(thread_id=thread_id, level=1).order_by('-creation_data')
    elif order == 'oldest':
        comments_root = Comment.objects.filter(thread_id=thread_id, level=1).order_by('creation_data')
    else:
        comments_root = Comment.objects.filter(thread_id=thread_id, level=1).order_by('-num_likes')
    replies = Reply.objects.filter(comment_root__in=comments_root)
    context = {'thread': thread, 'comments_root': comments_root, 'replies': replies, 'editat': edited, 'single': True}
    request.session['order'] = order
    return render(request, 'veure_thread.html', context)


def url_redireccio(request):
    next = request.POST.get('next', '/')
    if 'cercador' in next:
        keyword = request.POST.get('keyword', '')
        next = "{}?keyword={}".format(next, keyword)
    return next
