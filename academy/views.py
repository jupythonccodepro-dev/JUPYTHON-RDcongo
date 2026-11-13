from django.shortcuts import render

# Créez vos vues ici.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Academy

@api_view(['GET'])
def academy_list(request):
    data = list(Academy.objects.values())
    return Response(data)
