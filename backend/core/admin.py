from django.contrib import admin
from .models import (
    Tag, UserProfile, SegmentationRule, SegmentationResult,
    SegmentRule, SegmentRuleCondition, Department, Role,
    OperatorUserMapping, Segment,
)

admin.site.register(Tag)
admin.site.register(UserProfile)
admin.site.register(SegmentationRule)
admin.site.register(SegmentationResult)
admin.site.register(SegmentRule)
admin.site.register(SegmentRuleCondition)
admin.site.register(Department)
admin.site.register(Role)
admin.site.register(OperatorUserMapping)
admin.site.register(Segment)
