from django.urls import path
from .views import (
    MyProfileView,
    AdminUserListView,
    AdminUserDetailView,
    AdminRestoreUserView,
    AdminDeactivateUserView,
    GoogleLogin,
    PasswordResetRequestView, 
    PasswordResetConfirmView,
)

urlpatterns = [
    path("me/", MyProfileView.as_view(), name="my-profile"),

    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("admin/users/<int:pk>/restore/", AdminRestoreUserView.as_view(), name="admin-user-restore"),
    path("admin/users/<int:pk>/deactivate/", AdminDeactivateUserView.as_view(), name="admin-user-deactivate"),

    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]