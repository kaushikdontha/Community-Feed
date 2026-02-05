from rest_framework import serializers
from .models import Comment, CommentVote


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments with nested replies."""
    
    author = serializers.StringRelatedField(read_only=True)
    author_id = serializers.IntegerField(source='author.id', read_only=True)
    replies = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'author_id', 'post', 'parent',
            'vote_score', 'user_vote', 'is_deleted', 'reply_count',
            'replies', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'vote_score', 'is_deleted', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """Recursively serialize replies (limited depth)."""
        if obj.replies.exists():
            # Limit depth to prevent infinite recursion
            depth = self.context.get('depth', 0)
            if depth < 3:  # Max 3 levels deep
                context = {**self.context, 'depth': depth + 1}
                return CommentSerializer(
                    obj.replies.filter(is_deleted=False),
                    many=True,
                    context=context
                ).data
        return []
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = obj.votes.filter(user=request.user).first()
            return vote.vote_type if vote else None
        return None


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""
    
    class Meta:
        model = Comment
        fields = ['content', 'post', 'parent']
    
    def validate_parent(self, value):
        if value and value.post_id != self.initial_data.get('post'):
            raise serializers.ValidationError(
                "Parent comment must belong to the same post."
            )
        return value
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class CommentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for comment lists (no nested replies)."""
    
    author = serializers.StringRelatedField(read_only=True)
    user_vote = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'post', 'parent',
            'vote_score', 'user_vote', 'reply_count', 'created_at'
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
