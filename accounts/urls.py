from django.urls import path
from .views import (
    MyProfileView,
    AdminUserListView,
    AdminUserDetailView,
    AdminRestoreUserView,
    AdminDeactivateUserView,
    GoogleLogin,
)

urlpatterns = [
    path("me/", MyProfileView.as_view(), name="my-profile"),
    path("admin/users/", AdminUserListView.as_view()),
    path("admin/users/<int:pk>/", AdminUserDetailView.as_view()),
    path("admin/users/<int:pk>/restore/", AdminRestoreUserView.as_view()),
    path("admin/users/<int:pk>/deactivate/", AdminDeactivateUserView.as_view()),
    path("google/", GoogleLogin.as_view(), name="google_login"),
]