from rest_framework import generics, permissions
from .models import FeedbackMessage
from .serializers import FeedbackMessageSerializer


class FeedbackMessageCreateView(generics.CreateAPIView):
    queryset = FeedbackMessage.objects.all()
    serializer_class = FeedbackMessageSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
        
