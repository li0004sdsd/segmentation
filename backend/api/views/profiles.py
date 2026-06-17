from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import UserProfile, Tag
from api.serializers import UserProfileSerializer


class ProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.all().prefetch_related('tags').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all().prefetch_related('tags')
    serializer_class = UserProfileSerializer


class ProfileTagView(APIView):
    def post(self, request, pk):
        profile = UserProfile.objects.get(pk=pk)
        tag_id = request.data.get('tag_id')
        tag = Tag.objects.get(pk=tag_id)
        profile.tags.add(tag)
        return Response({'status': 'tag added'}, status=status.HTTP_200_OK)


class ProfileTagDeleteView(APIView):
    def delete(self, request, pk, tag_id):
        profile = UserProfile.objects.get(pk=pk)
        tag = Tag.objects.get(pk=tag_id)
        profile.tags.remove(tag)
        return Response({'status': 'tag removed'}, status=status.HTTP_200_OK)
