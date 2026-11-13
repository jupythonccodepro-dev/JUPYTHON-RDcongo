from django.urls import path

from .api import ContactAPIView

urlpatterns = [
    path('contact/', ContactAPIView.as_view(), name='contact'),
]
