from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Profile
from .serializers import ProfileSerializer, ProfileWithUserSerializer


class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current authenticated user's profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ProfileSerializer
        return ProfileWithUserSerializer
