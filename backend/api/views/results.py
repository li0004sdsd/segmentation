from rest_framework import generics
from core.models import SegmentationResult
from api.serializers import SegmentationResultSerializer


class ResultListView(generics.ListAPIView):
    queryset = SegmentationResult.objects.all().select_related('rule').order_by('-ran_at')
    serializer_class = SegmentationResultSerializer


class ResultDetailView(generics.RetrieveAPIView):
    queryset = SegmentationResult.objects.all().select_related('rule').prefetch_related('matched_profiles')
    serializer_class = SegmentationResultSerializer
