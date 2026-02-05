from rest_framework import serializers
from .models import Post, PostVote


class PostSerializer(serializers.ModelSerializer):
    """Full post serializer with author and community details."""
    
    author = serializers.StringRelatedField(read_only=True)
    community_name = serializers.CharField(source='community.name', read_only=True)
    community_slug = serializers.CharField(source='community.slug', read_only=True)
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'url', 'image', 'post_type',
            'author', 'community', 'community_name', 'community_slug',
            'vote_score', 'comment_count', 'user_vote',
            'is_pinned', 'is_locked', 'is_nsfw', 'is_spoiler',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'vote_score', 'comment_count',
            'created_at', 'updated_at'
        ]
    
    def get_user_vote(self, obj):
        """Get the current user's vote on this post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            return vote.vote_type if vote else None
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts."""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'url', 'image', 'post_type', 'community', 'is_nsfw', 'is_spoiler']
    
    def validate(self, attrs):
        post_type = attrs.get('post_type', 'text')
        
        if post_type == 'link' and not attrs.get('url'):
            raise serializers.ValidationError({'url': 'URL is required for link posts.'})
        
        if post_type == 'image' and not attrs.get('image'):
            raise serializers.ValidationError({'image': 'Image is required for image posts.'})
        
        return attrs
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for post lists."""
    
    author = serializers.StringRelatedField(read_only=True)
    community_name = serializers.CharField(source='community.name', read_only=True)
    community_slug = serializers.CharField(source='community.slug', read_only=True)
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'url', 'image', 'post_type',
            'author', 'community_name', 'community_slug',
            'vote_score', 'comment_count', 'user_vote',
            'is_pinned', 'is_nsfw', 'is_spoiler', 'created_at'
        ]
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            return vote.vote_type if vote else None
        return None


class VoteSerializer(serializers.Serializer):
    """Serializer for voting actions."""
    
    vote_type = serializers.ChoiceField(choices=['up', 'down'])
