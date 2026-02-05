from rest_framework import serializers
from .models import Community, CommunityMembership


class CommunitySerializer(serializers.ModelSerializer):
    """Serializer for community data."""
    
    creator = serializers.StringRelatedField(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = [
            'id', 'name', 'slug', 'description', 'rules',
            'banner', 'icon', 'creator', 'is_private',
            'member_count', 'is_member', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'creator', 'created_at']
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False


class CommunityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a community."""
    
    class Meta:
        model = Community
        fields = ['name', 'description', 'rules', 'is_private']
    
    def validate_name(self, value):
        # Ensure name only contains alphanumeric and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Name can only contain letters, numbers, and underscores."
            )
        return value
    
    def create(self, validated_data):
        from django.utils.text import slugify
        validated_data['slug'] = slugify(validated_data['name'])
        validated_data['creator'] = self.context['request'].user
        community = Community.objects.create(**validated_data)
        # Creator becomes first moderator and member
        community.moderators.add(validated_data['creator'])
        CommunityMembership.objects.create(
            user=validated_data['creator'],
            community=community
        )
        return community


class CommunityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for community lists."""
    
    member_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Community
        fields = ['id', 'name', 'slug', 'description', 'icon', 'member_count']
