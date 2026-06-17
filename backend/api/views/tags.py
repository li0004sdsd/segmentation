from rest_framework import generics
from core.models import Tag
from api.serializers import TagSerializer


class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all().order_by('-created_at')
    serializer_class = TagSerializer


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
