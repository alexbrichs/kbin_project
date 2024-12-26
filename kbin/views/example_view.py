from django.http import JsonResponse
from rest_framework.views import APIView


class Endpoint1View(APIView):
    def get(self, request):
        # Example respeñonse data
        data = {"message": "Hello World"}
        return JsonResponse(data)