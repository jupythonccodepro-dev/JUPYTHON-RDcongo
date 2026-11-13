from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .api import (
    LogoutAPIView, PasswordChangeAPIView, PasswordResetConfirmAPIView, PasswordResetRequestAPIView,
    ProfileAPIView, PublicProfileAPIView, RegisterAPIView, TokenObtainPairAPIView,
    UserFollowAPIView,
)
from .google_api import GoogleLoginAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairAPIView.as_view(), name='accounts_token_obtain_pair'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google-login/', GoogleLoginAPIView.as_view(), name='google_login'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('password/change/', PasswordChangeAPIView.as_view(), name='password_change'),
    path('password/reset/', PasswordResetRequestAPIView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    path('public-profile/<int:user_id>/', PublicProfileAPIView.as_view(), name='public_profile'),
    path('public-profile/<int:user_id>/follow/', UserFollowAPIView.as_view(), name='user_follow'),
]
