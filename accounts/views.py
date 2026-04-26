from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Profile
from .serializers import CombinedProfileSerializer


class MyProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or deactivate the current authenticated user's account/profile.

    This endpoint returns combined User + Profile data.

    Supported methods:
    - GET: view current user + profile data
    - PATCH: update user + profile data
    - DELETE: soft delete / deactivate current user account
    """
    serializer_class = CombinedProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete account by deactivating the user instead of deleting data.
        Profile and job applications remain in the database and can be restored by admin later.
        """
        user = request.user
        user.is_active = False
        user.save()

        return Response(
            {"detail": "Account has been deactivated successfully."},
            status=status.HTTP_200_OK,
        )