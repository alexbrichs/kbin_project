from django.shortcuts import redirect
from ..models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required(redirect_field_name='login')
@csrf_exempt
def votar_publicacio(request, thread_id):
    publicacio = Publicacio.objects.get(pk=thread_id)
    user = User.objects.get(email=request.user.email)

    if request.method == 'POST':
        tipus_vot = request.POST.get('vote_type')

        # Mirem si l'usuari ja ha votat
        if Vot.objects.filter(user=user, publicacio=publicacio).exists():
            vot = Vot.objects.get(user=user, publicacio=publicacio)

            if tipus_vot == 'positiu':
                if (vot.positiu):  # Si el vot ja era positiu eliminem el vot i actualitzem publicació
                    vot.delete()  # Eliminem el vot del sistema
                    publicacio.num_likes -= 1
                    publicacio.save()

                else:  # El vot passa a ser positiu perque abans era negatiu
                    publicacio.num_likes += 1
                    publicacio.num_dislikes -= 1
                    vot.positiu = True
                    vot.save()
                    publicacio.save()

            else:
                if (not vot.positiu):
                    vot.delete()  # Eliminem el vot del sistema
                    publicacio.num_dislikes -= 1
                    publicacio.save()

                else:  # El vot passa a ser negatiu
                    publicacio.num_dislikes += 1
                    publicacio.num_likes -= 1
                    vot.positiu = False
                    vot.save()
                    publicacio.save()
        else:  # Usuari encara no ha votat
            nou_vot = Vot(user=user, publicacio=publicacio, positiu=True)
            if tipus_vot == 'positiu':
                publicacio.num_likes += 1
                publicacio.save()
            else:
                publicacio.num_dislikes += 1
                nou_vot.positiu = False
                publicacio.save()
            nou_vot.save()
    return redirect(url_redireccio(request))


def url_redireccio(request):
    next = request.POST.get('next', '/')
    if 'cercador' in next:
        keyword = request.POST.get('keyword', '')
        next = "{}?keyword={}".format(next, keyword)
    return next
