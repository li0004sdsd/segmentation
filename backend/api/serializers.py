from django.contrib.auth.models import User
from rest_framework import serializers
from core.models import Tag, UserProfile, SegmentationRule, SegmentationResult


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserProfileSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, source='tags', required=False
    )

    class Meta:
        model = UserProfile
        fields = (
            'id', 'name', 'email', 'phone', 'age', 'gender', 'city', 'country',
            'tags', 'tag_ids', 'created_by', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')


class SegmentationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SegmentationRule
        fields = ('id', 'name', 'description', 'conditions', 'created_by', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')


class SegmentationResultSerializer(serializers.ModelSerializer):
    rule = SegmentationRuleSerializer(read_only=True)
    matched_profiles = UserProfileSerializer(many=True, read_only=True)

    class Meta:
        model = SegmentationResult
        fields = ('id', 'rule', 'matched_profiles', 'matched_count', 'ran_by', 'ran_at')
        read_only_fields = ('id', 'rule', 'matched_profiles', 'matched_count', 'ran_by', 'ran_at')
