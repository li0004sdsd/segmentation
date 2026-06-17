from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='profiles')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SegmentationRule(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    conditions = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SegmentationResult(models.Model):
    rule = models.ForeignKey(SegmentationRule, on_delete=models.CASCADE, related_name='results')
    matched_profiles = models.ManyToManyField(UserProfile, blank=True, related_name='segmentation_results')
    matched_count = models.PositiveIntegerField(default=0)
    ran_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='results')
    ran_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.rule.name} at {self.ran_at}"
