import re

from django.contrib.auth.password_validation import validate_password
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers

from .models import User

MAX_AVATAR_SIZE = 5 * 1024 * 1024
MAX_AVATAR_DIMENSION = 4096
AVATAR_FORMATS = {'JPEG', 'PNG', 'WEBP'}


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True, required=False, allow_blank=True)
    promotion = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'university', 'fullname', 'promotion']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value.lower()

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        fullname = validated_data.pop('fullname', '')
        promotion = validated_data.pop('promotion', '')
        first_name = ''
        last_name = ''
        if fullname:
            parts = fullname.strip().split(None, 1)
            first_name = parts[0]
            if len(parts) > 1:
                last_name = parts[1]

        username = validated_data.get('username') or validated_data.get('email')
        base_username = username
        counter = 0
        while User.objects.filter(username=username).exists():
            counter += 1
            username = f"{base_username}_{counter}"

        user = User.objects.create_user(
            username=username,
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            university=validated_data.get('university', ''),
            promotion=promotion,
        )

        if first_name or last_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value.lower()

    def validate_avatar(self, image_file):
        if image_file.size > MAX_AVATAR_SIZE:
            raise serializers.ValidationError('La photo ne doit pas dépasser 5 Mo.')

        try:
            image = Image.open(image_file)
            image_format = image.format
            width, height = image.size
            image.verify()
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
            raise serializers.ValidationError('Le fichier doit être une image valide.')
        finally:
            image_file.seek(0)

        if image_format not in AVATAR_FORMATS:
            raise serializers.ValidationError('Utilise une image JPEG, PNG ou WebP.')
        if width > MAX_AVATAR_DIMENSION or height > MAX_AVATAR_DIMENSION:
            raise serializers.ValidationError('La photo ne doit pas dépasser 4096 × 4096 pixels.')

        image_file.name = f'avatar.{image_format.lower()}'
        return image_file

    def update(self, instance, validated_data):
        previous_avatar = instance.avatar
        updated_instance = super().update(instance, validated_data)
        if previous_avatar and previous_avatar.name != updated_instance.avatar.name:
            previous_avatar.delete(save=False)
        return updated_instance

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'public_name',
            'bio',
            'avatar',
            'university',
            'promotion',
            'date_joined',
            'is_staff',
            'has_usable_password',
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'read_only': True},
            'is_staff': {'read_only': True},
            'date_joined': {'read_only': True},
            'has_usable_password': {'read_only': True},
        }


class PublicProfileSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='profile_display_name', read_only=True)
    avatar = serializers.SerializerMethodField()
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.SerializerMethodField()

    def get_is_following(self, user):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return user.followers.filter(follower=request.user).exists()

    def get_avatar(self, user):
        return user.avatar.url if user.avatar else ''

    class Meta:
        model = User
        fields = ['id', 'display_name', 'bio', 'avatar', 'follower_count', 'following_count', 'is_following']
        read_only_fields = fields
