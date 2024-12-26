from kbin.models.user import User


class AddUserToContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = None
        if request.user.is_authenticated:
            queryset = User.objects.filter(email=request.user.email)
            if queryset.exists():
                user = User.objects.get(email=request.user.email)

        request.usuari = user

        response = self.get_response(request)
        return response