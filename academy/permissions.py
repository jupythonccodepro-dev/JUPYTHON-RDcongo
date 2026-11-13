from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Allow full access to admin users, read-only for others."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):
    """Object-level permission to only allow owners of an object or admins to edit it."""

    def has_object_permission(self, request, view, obj):
        # Les requêtes peuvent lire les données.
        if request.method in SAFE_METHODS:
            return True
        # Seuls le propriétaire ou un membre du personnel peuvent modifier les données.
        return bool(getattr(request, 'user', None) and (request.user.is_staff or getattr(obj, 'user', None) == request.user))
