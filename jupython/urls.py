"""
URL configuration for jupython project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.api import TokenObtainPairAPIView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.http import Http404
from django.urls import re_path
from core.views import health_check

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),

    path('api/accounts/', include('accounts.urls')),
    path('api/', include('core.urls')),
    path('api/', include('academy.urls')),
    path('api/enrollments/', include('academy.enrollments_urls')),
    path('api/ranking/', include('ranking.urls')),
    # Points de terminaison des jetons (accès alternatif)
    path('api/token/', TokenObtainPairAPIView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Servir la page d’accueil du frontend à la racine du projet
    path('', TemplateView.as_view(template_name='index.html')),
]

# En développement, servir les fichiers statiques depuis le dossier des ressources du frontend.
urlpatterns += static('/images/', document_root=settings.BASE_DIR / 'frontend' / 'frontend' / 'images')
urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'frontend' / 'frontend' / 'assets')
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def _render_frontend_template(request, template_path):
    """Render an HTML template from the frontend folder if it exists, else 404.

    This allows serving files like /about.html or /academy/login.html using
    the templates located in frontend/frontend/.
    """
    # Sécurité : empêcher la traversée des répertoires.
    if '..' in template_path or template_path.startswith('/'):
        raise Http404()

    try:
        return render(request, template_path, {'GOOGLE_CLIENT_ID': getattr(settings, 'GOOGLE_CLIENT_ID', '')})
    except TemplateDoesNotExist:
        raise Http404()


# Servir directement les fichiers HTML du frontend (uniquement les fichiers .html).
# Garder ces routes après celles de l’API pour éviter toute interférence.
urlpatterns += [
    re_path(r'^(?P<template_path>.+\.html)$', _render_frontend_template),
]
 
