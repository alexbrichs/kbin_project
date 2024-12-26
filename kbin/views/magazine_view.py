from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from ..models import *
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def all_magazines(request, ordre=None):
    magazines = Magazine.objects.all()
    if request.user.is_authenticated:
        user_email = request.user.email
        user = User.objects.get(email=user_email)
        user_subscriptions = Subscription.objects.filter(user=user).values_list('magazine_id', flat=True)
    else:
        user_subscriptions = []
    if ordre == 'threads':
        magazines = sorted(magazines, key=lambda x: x.total_threads(), reverse=True)
    elif ordre == 'elements':
        magazines = sorted(magazines, key=lambda x: x.total_publicacions(), reverse=True)
    elif ordre == 'commented':
        magazines = sorted(magazines, key=lambda x: x.total_comments(), reverse=True)
    elif ordre == 'suscriptions':
        magazines = sorted(magazines, key=lambda x: x.n_suscriptions, reverse=True)
    context = {'magazines': magazines, 'user_subscriptions': user_subscriptions}
    template = loader.get_template("all_magazines.html")
    return HttpResponse(template.render(context, request))


@login_required(redirect_field_name='login')
@csrf_exempt
def new_magazine(request):
    if request.method == 'POST':

        name = request.POST.get('name')
        if Magazine.objects.filter(name=name).exists():
            is_used = True
            context = {'is_used': is_used}
            return render(request, 'new_magazine.html', context)
        else:
            author_email = request.user.email
            author = User.objects.get(email=author_email)
            creation_date = timezone.now().isoformat()
            title = request.POST.get('title')
            description = request.POST.get('description')
            rules = request.POST.get('rules')
            nsfw = request.POST.get('isAdult')

            magazine = Magazine.objects.create(
                name=name,
                author=author,
                creation_date=creation_date,
                title=title,
                description=description,
                rules=rules,
                nsfw=nsfw
            )

            return redirect('main')
    else:
        template = loader.get_template("new_magazine.html")
        return HttpResponse(template.render({}, request))


@login_required(redirect_field_name='login')
@csrf_exempt
def add_subscription(request, magazine_id):
    if request.method == 'POST':
        user = User.objects.get(email=request.user.email)
        magazine = Magazine.objects.get(pk=magazine_id)
        sub = Subscription.objects.create(user=user, magazine=magazine)
        sub.save()
        magazine.n_suscriptions += 1
        magazine.save()
        return redirect('all_magazines')
    else:
        return redirect('main')


@login_required(redirect_field_name='login')
@csrf_exempt
def remove_subscription(request, magazine_id):
    if request.method == 'POST':
        user = User.objects.get(email=request.user.email)
        magazine = Magazine.objects.get(pk=magazine_id)
        Subscription.objects.filter(user=user, magazine=magazine).delete()
        magazine.n_suscriptions -= 1
        magazine.save()
        return redirect('all_magazines')
    else:
        return redirect('main')


def veure_magazine(request, magazine_id, ordre=None, filter=None):
    if ordre == None:
        ordre = 'newest'
    magazine = Magazine.objects.get(pk=magazine_id)
    links = Link.objects.filter(magazine_id=magazine_id)
    threads = Thread.objects.filter(magazine_id=magazine_id)

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
    elif ordre == 'comment':
        tot = sorted(tot, key=lambda x: x.num_coments, reverse=True)

    context = {'magazine': magazine, 'threads': tot, 'active_filter': filter, 'ordre': ordre}
    return render(request, 'veure_magazine.html', context)
