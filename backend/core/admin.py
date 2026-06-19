from django.contrib import admin
from .models import Tag, UserProfile, SegmentationRule, SegmentationResult, SegmentRule, SegmentRuleCondition

admin.site.register(Tag)
admin.site.register(UserProfile)
admin.site.register(SegmentationRule)
admin.site.register(SegmentationResult)
admin.site.register(SegmentRule)
admin.site.register(SegmentRuleCondition)
