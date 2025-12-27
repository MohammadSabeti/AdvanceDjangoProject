from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadonly(BasePermission):
    message = "You are not the owner of this post."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author.user == request.user
