from django.core.exceptions import PermissionDenied
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import Segment
from core.services import SegmentUserQueryService, SEGMENT_NOT_FOUND_CODE
from api.serializers import SegmentSerializer, UserProfileSerializer


class SegmentListCreateView(generics.ListCreateAPIView):
    queryset = Segment.objects.all().order_by('-created_at')
    serializer_class = SegmentSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SegmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer


class UserSegmentController(APIView):
    def get(self, request, segmentId):
        qs = SegmentUserQueryService.listUsers(segment_id=segmentId, request_user=request.user)
        if qs is None:
            return Response(
                {'code': SEGMENT_NOT_FOUND_CODE, 'message': 'Segment not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserProfileSerializer(qs, many=True)
        return Response({
            'segment_id': segmentId,
            'count': len(serializer.data),
            'results': serializer.data,
        })
