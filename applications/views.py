from rest_framework import generics, permissions

from .models import JobApplication
from .serializers import (
    JobApplicationSerializer,
    JobApplicationCreateUpdateSerializer,
)


class JobApplicationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = JobApplication.objects.filter(user=self.request.user).order_by("-created_at")

        status_param = self.request.query_params.get("status")
        source_platform = self.request.query_params.get("source_platform")
        is_active = self.request.query_params.get("is_active")

        if status_param:
            queryset = queryset.filter(status=status_param)

        if source_platform:
            queryset = queryset.filter(source_platform=source_platform)

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return JobApplicationCreateUpdateSerializer
        return JobApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JobApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return JobApplicationCreateUpdateSerializer
        return JobApplicationSerializer


class KanbanJobApplicationView(generics.ListAPIView):
    """
    Returns all current user's job applications.
    Frontend can group them by status into Kanban columns.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).order_by("-updated_at")
