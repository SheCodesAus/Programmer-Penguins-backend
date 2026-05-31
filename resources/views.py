from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .metadata import MetadataError, extract_chatgpt_shared_metadata, extract_url_metadata
from .models import Resource
from .serializers import ResourceSerializer


class ResourceListCreateView(generics.ListCreateAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resource.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resource.objects.filter(user=self.request.user)


class ResourceMetadataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        url = request.data.get("url", "").strip()

        if not url:
            return Response(
                {"url": "URL is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            metadata = extract_url_metadata(url)
        except MetadataError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(metadata)


class ChatGPTResourceMetadataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        url = request.data.get("url", "").strip()

        if not url:
            return Response(
                {"url": "URL is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            metadata = extract_chatgpt_shared_metadata(url)
        except MetadataError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(metadata)
