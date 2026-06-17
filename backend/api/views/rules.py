from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import SegmentationRule, UserProfile, SegmentationResult
from api.serializers import SegmentationRuleSerializer, SegmentationResultSerializer


def apply_conditions(conditions):
    qs = UserProfile.objects.prefetch_related('tags')
    if 'age_min' in conditions:
        qs = qs.filter(age__gte=conditions['age_min'])
    if 'age_max' in conditions:
        qs = qs.filter(age__lte=conditions['age_max'])
    if 'gender' in conditions and conditions['gender']:
        qs = qs.filter(gender=conditions['gender'])
    if 'city' in conditions and conditions['city']:
        qs = qs.filter(city__icontains=conditions['city'])
    if 'country' in conditions and conditions['country']:
        qs = qs.filter(country__icontains=conditions['country'])
    if 'tags' in conditions and conditions['tags']:
        for tag_id in conditions['tags']:
            qs = qs.filter(tags__id=tag_id)
    return qs.distinct()


class RuleListCreateView(generics.ListCreateAPIView):
    queryset = SegmentationRule.objects.all().order_by('-created_at')
    serializer_class = SegmentationRuleSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SegmentationRule.objects.all()
    serializer_class = SegmentationRuleSerializer


class RuleRunView(APIView):
    def post(self, request, pk):
        rule = SegmentationRule.objects.get(pk=pk)
        matched = apply_conditions(rule.conditions)
        result = SegmentationResult.objects.create(
            rule=rule,
            matched_count=matched.count(),
            ran_by=request.user,
        )
        result.matched_profiles.set(matched)
        serializer = SegmentationResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
