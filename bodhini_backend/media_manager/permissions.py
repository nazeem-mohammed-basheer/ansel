# media_manager/permissions.py

from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin (staff) users to create, update, or delete objects.
    Read-only access is allowed for any request (authenticated or not).
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff

class IsAuthenticatedAndAdmin(permissions.BasePermission):
    """
    Custom permission to only allow authenticated admin (staff) users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
