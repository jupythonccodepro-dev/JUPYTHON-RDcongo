from django.db.models import Count, F, Q
import logging

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import User, UserFollow
from .serializers import PublicProfileSerializer, RegisterSerializer, UserSerializer


class TokenObtainPairAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        identifier = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')

        if (
            not isinstance(identifier, str)
            or not isinstance(password, str)
            or not identifier.strip()
            or not password
        ):
            raise AuthenticationFailed('Veuillez fournir un email ou un nom d’utilisateur et un mot de passe.')

        identifier = identifier.strip()
        user = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
        if not user or not user.is_active or not user.check_password(password):
            raise AuthenticationFailed('Identifiants invalides.')

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        user_data = UserSerializer(user).data

        return Response({
            'message': 'Utilisateur créé',
            'user': user_data,
            'access': access_token,
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset'

    def post(self, request):
        email = request.data.get('email')
        if not isinstance(email, str):
            return Response({'email': ['Saisis une adresse e-mail valide.']}, status=status.HTTP_400_BAD_REQUEST)
        email = email.strip()
        try:
            validate_email(email)
        except DjangoValidationError:
            return Response({'email': ['Saisis une adresse e-mail valide.']}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user and user.has_usable_password():
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri('/academy/reset-password.html')
            reset_url = f'{reset_url}?uid={uid}&token={token}'
            message = (
                f'Bonjour {user.profile_display_name},\n\n'
                'Pour choisir un nouveau mot de passe Jupython, ouvre ce lien :\n'
                f'{reset_url}\n\n'
                'Si tu n’as pas demandé cette modification, ignore ce message.'
            )
            try:
                send_mail(
                    'Réinitialiser ton mot de passe Jupython',
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception:
                logging.getLogger(__name__).exception('Échec de l’envoi du lien de réinitialisation Jupython.')

        if (
            settings.DEBUG
            and settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'
        ):
            message = (
                'Le site local n’envoie pas de courriels. Si cette adresse correspond à un compte, '
                'le lien de réinitialisation est affiché dans le terminal où Django fonctionne.'
            )
        else:
            message = 'Si un compte actif utilise cette adresse, un lien de réinitialisation lui sera envoyé.'

        return Response({'message': message}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset'

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')
        confirmation = request.data.get('confirm_password')
        if not all(isinstance(value, str) and value for value in (uid, token, password, confirmation)):
            return Response({'error': 'Complète tous les champs.'}, status=status.HTTP_400_BAD_REQUEST)
        if password != confirmation:
            return Response({'confirm_password': ['Les mots de passe ne correspondent pas.']}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, DjangoValidationError, User.DoesNotExist):
            return Response({'error': 'Ce lien est invalide ou a expiré.'}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Ce lien est invalide ou a expiré.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password, user=user)
        except DjangoValidationError as error:
            return Response({'password': list(error.messages)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save(update_fields=['password'])
        for outstanding in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding)
        return Response({'message': 'Mot de passe modifié. Tu peux maintenant te connecter.'})


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_change'

    def post(self, request):
        current_password = request.data.get('current_password')
        password = request.data.get('password')
        confirmation = request.data.get('confirm_password')
        required_values = (password, confirmation)
        if request.user.has_usable_password():
            required_values += (current_password,)
        if not all(isinstance(value, str) and value for value in required_values):
            return Response({'error': 'Compl?te tous les champs.'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.has_usable_password() and not request.user.check_password(current_password):
            return Response({'current_password': ['Le mot de passe actuel est incorrect.']}, status=status.HTTP_400_BAD_REQUEST)
        if password != confirmation:
            return Response({'confirm_password': ['Les mots de passe ne correspondent pas.']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(password, user=request.user)
        except DjangoValidationError as error:
            return Response({'password': list(error.messages)}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(password)
        request.user.save(update_fields=['password'])
        refresh = RefreshToken.for_user(request.user)
        for outstanding in OutstandingToken.objects.filter(user=request.user).exclude(jti=str(refresh['jti'])):
            BlacklistedToken.objects.get_or_create(token=outstanding)
        return Response({
            'message': 'Mot de passe modifié.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PublicProfileAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(
            User.objects.annotate(
                follower_count=Count('followers', distinct=True),
                following_count=Count('following', distinct=True),
            ),
            pk=user_id,
            is_active=True,
        )
        return Response(PublicProfileSerializer(user, context={'request': request}).data)


class UserFollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        followed = get_object_or_404(User, pk=user_id, is_active=True)
        if followed.pk == request.user.pk:
            return Response(
                {'detail': 'Tu ne peux pas suivre ton propre profil.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        UserFollow.objects.get_or_create(follower=request.user, followed=followed)
        return Response({
            'is_following': True,
            'follower_count': followed.followers.count(),
        }, status=status.HTTP_200_OK)

    def delete(self, request, user_id):
        followed = get_object_or_404(User, pk=user_id, is_active=True)
        UserFollow.objects.filter(follower=request.user, followed=followed).delete()
        return Response({
            'is_following': False,
            'follower_count': followed.followers.count(),
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Jeton de renouvellement manquant.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            if str(token['user_id']) != str(request.user.pk):
                return Response(
                    {'error': 'Ce jeton n’appartient pas à cet utilisateur.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            token.blacklist()
        except (TokenError, KeyError):
            return Response(
                {'error': 'Jeton de renouvellement invalide.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'message': 'Déconnexion réussie'}, status=status.HTTP_200_OK)
