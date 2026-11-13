try:
    import requests
    _REQUESTS_AVAILABLE = True
except Exception:
    requests = None
    _REQUESTS_AVAILABLE = False

import os
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from .models import Certificate, Formation
from .certificates_serializers import CertificateSerializer
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

MAX_CERTIFICATE_SIZE = 10 * 1024 * 1024
CERTIFICATE_IMAGE_FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.png': 'PNG',
    '.webp': 'WEBP',
}
MAX_CERTIFICATE_IMAGE_PIXELS = 40_000_000


def validate_certificate_file(upload):
    if upload.size > MAX_CERTIFICATE_SIZE:
        return 'Le fichier ne doit pas dépasser 10 Mo.'

    extension = Path(upload.name).suffix.lower()
    if extension == '.pdf':
        upload.seek(0)
        valid = upload.read(5) == b'%PDF-'
        upload.seek(0)
        return None if valid else 'Le fichier PDF est invalide.'

    expected_format = CERTIFICATE_IMAGE_FORMATS.get(extension)
    if not expected_format:
        return 'Utilise un fichier PDF, JPEG, PNG ou WebP.'

    try:
        image = Image.open(upload)
        image_format = image.format
        if image.width * image.height > MAX_CERTIFICATE_IMAGE_PIXELS:
            return 'L’image ne doit pas dépasser 40 mégapixels.'
        image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        return 'Le fichier image est invalide.'
    finally:
        upload.seek(0)

    if image_format != expected_format:
        return 'L’extension du fichier ne correspond pas à son format réel.'
    return None


def certificate_file_response(certificate):
    if not certificate.certificate_file:
        raise Http404

    extension = Path(certificate.certificate_file.name).suffix.lower()
    content_type = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
    }.get(extension)
    if not content_type:
        raise Http404

    try:
        file_handle = certificate.certificate_file.open('rb')
    except FileNotFoundError as exc:
        raise Http404 from exc
    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=f'certificate-{certificate.id}{extension}',
        content_type=content_type,
    )


def send_n8n_event(event_name, payload):
    url = os.environ.get('N8N_WEBHOOK_URL')
    if not url:
        return False
    if not _REQUESTS_AVAILABLE:
        # La bibliothèque requests est indisponible : impossible d’envoyer le webhook.
        return False
    try:
        requests.post(url, json={'event': event_name, 'payload': payload}, timeout=5)
        return True
    except Exception:
        return False


class SubmitCertificateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def post(self, request):
        # Accepte un lien HTTPS ou un justificatif privé téléversé.
        formation_id = request.data.get('formation_id')
        certificate_url = request.data.get('certificate_url') or ''
        certificate_file = request.FILES.get('certificate_file')
        if not formation_id:
            return Response({'error': 'formation_id requis'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(certificate_url, str):
            return Response(
                {'error': 'Le lien du certificat doit être une chaîne de caractères.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        certificate_url = certificate_url.strip()
        if bool(certificate_url) == bool(certificate_file):
            return Response(
                {'error': 'Ajoutez soit un lien HTTPS, soit un fichier de certificat.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            formation = Formation.objects.get(id=formation_id)
        except (Formation.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Formation non trouvée'}, status=status.HTTP_404_NOT_FOUND)

        if formation.hosted_by_jupython:
            return Response(
                {
                    'error': (
                        'Ce parcours suit ta progression dans Jupython, mais ne délivre pas de certificat. '
                        'Les certificats doivent être obtenus auprès des organismes qui les émettent.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if certificate_url:
            if len(certificate_url) > 200:
                return Response(
                    {'error': 'Le lien du certificat doit contenir au maximum 200 caractères'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                URLValidator(schemes=['https'])(certificate_url)
            except (ValidationError, TypeError):
                return Response(
                    {'error': 'Le lien du certificat doit être une URL HTTPS valide'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if certificate_file:
            file_error = validate_certificate_file(certificate_file)
            if file_error:
                return Response({'error': file_error}, status=status.HTTP_400_BAD_REQUEST)

        if Certificate.objects.filter(user=request.user, formation=formation).exists():
            return Response(
                {'error': 'Un certificat a déjà été soumis pour cette formation'},
                status=status.HTTP_409_CONFLICT,
            )

        cert = Certificate.objects.create(
            user=request.user,
            formation=formation,
            certificate_url=certificate_url,
            certificate_file=certificate_file or '',
        )
        send_n8n_event(
            'certificate_submitted',
            {
                'certificate_id': cert.id,
                'user_id': request.user.id,
                'formation_id': formation.id,
                'has_file': bool(cert.certificate_file),
            },
        )

        serializer = CertificateSerializer(cert)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyCertificatesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        certs = Certificate.objects.filter(user=request.user)
        serializer = CertificateSerializer(certs, many=True)
        return Response(serializer.data)


class CertificateFileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, certificate_id):
        certificates = Certificate.objects.filter(pk=certificate_id)
        if not request.user.is_staff:
            certificates = certificates.filter(user=request.user)
        certificate = certificates.first()
        if not certificate or not certificate.certificate_file:
            raise Http404
        return certificate_file_response(certificate)
