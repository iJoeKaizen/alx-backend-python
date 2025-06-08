from rest_framework import permissions

class IsMessageOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # For messages: access only if user is sender
        return obj.sender == request.user

class IsConversationParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # For conversations: access only if user is a participant
        return request.user in obj.participants.all()
