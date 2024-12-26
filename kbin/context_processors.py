def usuari_context_processor(request):
    return {'usuari': getattr(request, 'usuari', None)}