from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import SegmentationRule, SegmentRule, UserProfile, SegmentationResult
from core.services import SegmentRuleService, PriorityConflictError, PRIORITY_CONFLICT_CODE
from api.serializers import (
    SegmentationRuleSerializer, SegmentationResultSerializer,
    SegmentRuleSerializer,
)


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


class SegmentRuleListView(APIView):
    def get(self, request):
        rules = SegmentRule.objects.all().prefetch_related('segment_rule_conditions')
        serializer = SegmentRuleSerializer(rules, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SegmentRuleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        conditions_data = request.data.get('segment_rule_conditions', [])

        try:
            rule = SegmentRuleService.saveRule(
                rule_data=serializer.validated_data,
                conditions_data=conditions_data,
                user=request.user,
            )
        except PriorityConflictError as e:
            return Response(
                {'code': e.code, 'message': e.message, 'detail': 'priority value already exists'},
                status=status.HTTP_409_CONFLICT,
            )

        output_serializer = SegmentRuleSerializer(rule)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class SegmentRuleDetailView(APIView):
    def get(self, request, pk):
        try:
            rule = SegmentRule.objects.prefetch_related('segment_rule_conditions').get(pk=pk)
        except SegmentRule.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SegmentRuleSerializer(rule)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            rule = SegmentRule.objects.get(pk=pk)
        except SegmentRule.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SegmentRuleSerializer(rule, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        conditions_data = request.data.get('segment_rule_conditions', [])

        try:
            updated_rule = SegmentRuleService.saveRule(
                rule_data=serializer.validated_data,
                conditions_data=conditions_data,
                rule_instance=rule,
            )
        except PriorityConflictError as e:
            return Response(
                {'code': e.code, 'message': e.message, 'detail': 'priority value already exists'},
                status=status.HTTP_409_CONFLICT,
            )

        output_serializer = SegmentRuleSerializer(updated_rule)
        return Response(output_serializer.data)

    def patch(self, request, pk):
        try:
            rule = SegmentRule.objects.get(pk=pk)
        except SegmentRule.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SegmentRuleSerializer(rule, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        conditions_data = request.data.get('segment_rule_conditions', [])

        try:
            updated_rule = SegmentRuleService.saveRule(
                rule_data=serializer.validated_data,
                conditions_data=conditions_data,
                rule_instance=rule,
            )
        except PriorityConflictError as e:
            return Response(
                {'code': e.code, 'message': e.message, 'detail': 'priority value already exists'},
                status=status.HTTP_409_CONFLICT,
            )

        output_serializer = SegmentRuleSerializer(updated_rule)
        return Response(output_serializer.data)

    def delete(self, request, pk):
        try:
            rule = SegmentRule.objects.get(pk=pk)
        except SegmentRule.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
