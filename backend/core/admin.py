from django.contrib import admin
from .models import Tag, UserProfile, SegmentationRule, SegmentationResult

admin.site.register(Tag)
admin.site.register(UserProfile)
admin.site.register(SegmentationRule)
admin.site.register(SegmentationResult)
