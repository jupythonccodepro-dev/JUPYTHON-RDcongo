from rest_framework.routers import DefaultRouter
from .api import FormationViewSet

router = DefaultRouter()
router.register('formations', FormationViewSet, basename='formation')

urlpatterns = router.urls

# Routes des certificats
from django.urls import path
from .certificates_api import CertificateFileAPIView, SubmitCertificateAPIView, MyCertificatesAPIView

urlpatterns += [
	path('certificates/submit/', SubmitCertificateAPIView.as_view()),
	path('certificates/my/', MyCertificatesAPIView.as_view()),
	path('certificates/<int:certificate_id>/file/', CertificateFileAPIView.as_view()),
]
