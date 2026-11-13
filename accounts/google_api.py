import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

# Importer les bibliothèques Google à la demande ; si elles manquent, renvoyer une erreur explicite sans interrompre le serveur.
try:
    import google.oauth2.id_token as _google_id_token
    import google.auth.transport.requests as _google_requests
    _GOOGLE_AVAILABLE = True
except Exception:
    _GOOGLE_AVAILABLE = False


class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not _GOOGLE_AVAILABLE:
            return Response({'error': 'Le package google-auth est manquant. Exécutez `pip install google-auth` ou `pip install -r requirements.txt`.'}, status=status.HTTP_501_NOT_IMPLEMENTED)

        id_token = request.data.get('id_token') or request.data.get('credential')
        if not id_token:
            return Response({'error': 'id_token requis'}, status=status.HTTP_400_BAD_REQUEST)

        client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)
        if not client_id:
            return Response({'error': 'Google n’est pas encore configuré sur ce serveur. Ajoutez GOOGLE_CLIENT_ID pour activer la connexion Google.'}, status=status.HTTP_501_NOT_IMPLEMENTED)

        try:
            request_adapter = _google_requests.Request()
            id_info = _google_id_token.verify_oauth2_token(id_token, request_adapter, audience=client_id)
        except ValueError as exc:
            reason = str(exc).lower()
            if 'audience' in reason or 'recipient' in reason:
                logger.warning('Google ID token rejected because its audience does not match.')
                return Response(
                    {
                        'error': 'Le client Google ne correspond pas à celui configuré sur Jupython. Vérifie GOOGLE_CLIENT_ID et le client OAuth utilisé.',
                        'code': 'google_client_mismatch',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if 'expired' in reason:
                logger.warning('Google ID token rejected because it has expired.')
                return Response(
                    {
                        'error': 'Le jeton Google a expiré. Ferme la fenêtre Google et recommence la connexion.',
                        'code': 'google_token_expired',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if 'too early' in reason or 'future' in reason:
                logger.warning('Google ID token rejected because its issue time is in the future.')
                return Response(
                    {
                        'error': 'L’heure du jeton Google est trop en avance. Vérifie la date et l’heure de l’ordinateur.',
                        'code': 'google_token_time_invalid',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            logger.warning('Google ID token rejected by verification (%s).', type(exc).__name__)
            return Response(
                {
                    'error': 'Google a refusé le jeton. Vérifie l’origine autorisée et le client OAuth, puis réessaie.',
                    'code': 'google_token_invalid',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except _google_id_token.exceptions.TransportError:
            logger.exception('Google ID token could not be verified because Google is unreachable.')
            return Response(
                {
                    'error': 'Le serveur ne peut pas joindre Google pour vérifier la connexion. Réessaie dans quelques instants.',
                    'code': 'google_verification_unavailable',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # id_info contient l’adresse e-mail et sub (l’identifiant utilisateur Google).
        email = id_info.get('email')
        if not email:
            return Response({'error': 'Email Google manquant'}, status=status.HTTP_400_BAD_REQUEST)
        if id_info.get('email_verified') is not True:
            return Response(
                {'error': 'Google doit avoir vérifié cette adresse e-mail avant la connexion.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized_username = email.split('@')[0]
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            username = email
            counter = 0
            while User.objects.filter(username=username).exists():
                counter += 1
                username = f"{normalized_username}_{counter}"

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=id_info.get('given_name', ''),
                last_name=id_info.get('family_name', ''),
            )
        elif not user.is_active:
            return Response(
                {'error': 'Ce compte est désactivé. Contacte un administrateur.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Connexion Google réussie',
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)
