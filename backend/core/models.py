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
    DATA_SCOPE_CHOICES = [
        ('all', 'All'),
        ('dept', 'Department'),
        ('self', 'Self'),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    data_scope = models.CharField(max_length=20, choices=DATA_SCOPE_CHOICES, default='dept')
    tags = models.ManyToManyField(Tag, blank=True, related_name='profiles')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.name


class Role(models.Model):
    ROLE_ADMIN = 'ROLE_ADMIN'
    ROLE_ANALYST = 'ROLE_ANALYST'
    ROLE_OPERATOR = 'ROLE_OPERATOR'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_ANALYST, 'Analyst'),
        (ROLE_OPERATOR, 'Operator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_OPERATOR)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_roles'

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class OperatorUserMapping(models.Model):
    operator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operator_assignments')
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='operator_links')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'operator_user_mapping'
        unique_together = [('operator', 'user_profile')]

    def __str__(self):
        return f"Operator {self.operator.username} -> UserProfile {self.user_profile.id}"


class Segment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(UserProfile, blank=True, related_name='segments')
    rule = models.ForeignKey('SegmentRule', on_delete=models.SET_NULL, null=True, blank=True, related_name='segments')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_segments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'segments'

    def __str__(self):
        return self.name


class SegmentRule(models.Model):
    rule_id = models.CharField(max_length=100, unique=True)
    rule_name = models.CharField(max_length=200)
    conditions = models.JSONField(default=dict)
    priority = models.PositiveIntegerField(unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='segment_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'segment_rules'
        ordering = ['priority']

    def __str__(self):
        return self.rule_name


class SegmentRuleCondition(models.Model):
    CONDITION_TYPE_CHOICES = [
        ('age', 'Age'),
        ('gender', 'Gender'),
        ('city', 'City'),
        ('country', 'Country'),
        ('tag', 'Tag'),
        ('custom', 'Custom'),
    ]

    rule = models.ForeignKey(SegmentRule, on_delete=models.CASCADE, related_name='segment_rule_conditions')
    field = models.CharField(max_length=100)
    operator = models.CharField(max_length=50)
    value = models.JSONField(default=dict)
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPE_CHOICES, default='custom')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'segment_rule_conditions'

    def __str__(self):
        return f"{self.rule.rule_name} - {self.field} {self.operator}"


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
