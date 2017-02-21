from rest_framework import permissions


class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser


class IsOrderChatParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in [obj.sender_id, obj.recipient_id]


class IsOrderOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.customer