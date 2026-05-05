from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.hashers import make_password
from django.conf import settings
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
    
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

User = get_user_model()


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip()

        if not email:
            return Response(
                {"email": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Always return the same message for security reasons.
        # This prevents people from checking whether an email exists.
        success_message = {
            "detail": "If this email exists, a password reset link has been sent."
        }

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(success_message, status=status.HTTP_200_OK)

        token_generator = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        send_mail(
            subject="Reset your JobTracker password",
            message=f"Click the link below to reset your password:\n\n{reset_link}",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(success_message, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("password")

        if not uid or not token or not new_password:
            return Response(
                {"detail": "UID, token and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
        except Exception:
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_generator = PasswordResetTokenGenerator()

        if not token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.password = make_password(new_password)
        user.save()

        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )