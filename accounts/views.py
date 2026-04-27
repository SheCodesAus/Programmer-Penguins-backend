from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .serializers import CombinedProfileSerializer, AdminProfileSerializer


class MyProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CombinedProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def destroy(self, request, *args, **kwargs):
        request.user.is_active = False
        request.user.save()

        return Response(
            {"detail": "Account has been deactivated successfully."},
            status=status.HTTP_200_OK,
        )


class AdminUserListView(generics.ListAPIView):
    queryset = Profile.objects.select_related("user")
    serializer_class = AdminProfileSerializer
    permission_classes = [IsAdminUser]


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.select_related("user")
    serializer_class = AdminProfileSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["get", "patch"]


class AdminRestoreUserView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        profile = Profile.objects.select_related("user").get(pk=pk)
        profile.user.is_active = True
        profile.user.save()

        return Response({"detail": "User restored successfully."})


class AdminDeactivateUserView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        profile = Profile.objects.select_related("user").get(pk=pk)
        profile.user.is_active = False
        profile.user.save()

        return Response({"detail": "User deactivated successfully."})