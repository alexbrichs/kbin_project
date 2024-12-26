from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.db.models import Q
from ..models import *
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def view_cercador(request,ordre=None,filter=None):

    if request.method == 'POST':
        keyword = request.POST.get('keyword')
    else:
        keyword = request.GET.get('keyword')

    if (keyword == None or (all(char.isspace() for char in keyword))): #Mostrem només el camp per fer la cerca
        template = loader.get_template('cercador.html')
        return HttpResponse(template.render({}, request=request))

    else: #Busquem totes les publicacions que contenen en el titol i el cos la keyword indicada
        links = Link.objects.filter(Q(title__contains=keyword) | Q(body__contains=keyword))
        threads = Thread.objects.filter(Q(title__contains=keyword) | Q(body__contains=keyword))

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

        context = {'threads': tot, 'active_option': ordre, 'active_filter': filter,'es_cerca': True, 'num_publicacions': len(tot)}


        template = loader.get_template('cercador.html')
        return HttpResponse(template.render(context, request=request))

 #   else:
 #       print("No Es un post")
 #       keyword = request.GET.get('keyword')
 #       print(keyword)
 #       template = loader.get_template('cercador.html')

  #      return HttpResponse(template.render({},request))


