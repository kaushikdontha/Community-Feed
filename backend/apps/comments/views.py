from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.db.models import F, Prefetch
from .models import Comment, CommentVote
from .serializers import (
    CommentSerializer,
    CommentCreateSerializer,
    CommentListSerializer,
    VoteSerializer,
)


def get_prefetched_comments_queryset(base_queryset):
    """
    Prefetch nested comments up to 3 levels deep to solve N+1 problem.
    Instead of triggering 50 queries for 50 comments, this uses just a few queries.
    """
    # Level 1 replies
    level1_prefetch = Prefetch(
        'replies',
        queryset=Comment.objects.filter(is_deleted=False).select_related('author')
    )
    
    # Level 2 replies (replies to replies)
    level2_prefetch = Prefetch(
        'replies__replies',
        queryset=Comment.objects.filter(is_deleted=False).select_related('author')
    )
    
    # Level 3 replies (deepest level)
    level3_prefetch = Prefetch(
        'replies__replies__replies',
        queryset=Comment.objects.filter(is_deleted=False).select_related('author')
    )
    
    return base_queryset.prefetch_related(
        level1_prefetch,
        level2_prefetch,
        level3_prefetch,
        'votes',  # Prefetch votes for user_vote calculation
        'replies__votes',
        'replies__replies__votes',
    )


class CommentListCreateView(generics.ListCreateAPIView):
    """List comments for a post or create a new comment."""
    
    def get_queryset(self):
        queryset = Comment.objects.filter(is_deleted=False).select_related('author')
        
        # Filter by post
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id, parent__isnull=True)
        
        # Sort option
        sort = self.request.query_params.get('sort', 'best')
        if sort == 'best':
            queryset = queryset.order_by('-vote_score', '-created_at')
        elif sort == 'new':
            queryset = queryset.order_by('-created_at')
        elif sort == 'old':
            queryset = queryset.order_by('created_at')
        elif sort == 'controversial':
            queryset = queryset.order_by('-vote_score')
        
        # Apply N+1 optimization with prefetch
        queryset = get_prefetched_comments_queryset(queryset)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a comment."""
    
    queryset = Comment.objects.filter(is_deleted=False)
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own comments.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own comments.")
        # Soft delete to preserve thread structure
        instance.is_deleted = True
        instance.content = "[deleted]"
        instance.save()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def vote_comment(request, pk):
    """
    Upvote or downvote a comment with ATOMIC transaction to prevent race conditions.
    Uses select_for_update to lock the vote row during the transaction.
    """
    from apps.users.models import KarmaTransaction
    
    serializer = VoteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    vote_type = serializer.validated_data['vote_type']
    
    # Use atomic transaction to prevent race conditions
    with transaction.atomic():
        try:
            # Lock the comment row to prevent concurrent modifications
            comment = Comment.objects.select_for_update().get(pk=pk, is_deleted=False)
        except Comment.DoesNotExist:
            return Response(
                {'error': 'Comment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Try to get existing vote with lock
        existing_vote = CommentVote.objects.select_for_update().filter(
            user=request.user, 
            comment=comment
        ).first()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Same vote - remove it (toggle off)
                old_vote_type = existing_vote.vote_type
                existing_vote.delete()
                
                # Update vote score atomically
                if old_vote_type == 'up':
                    Comment.objects.filter(pk=pk).update(vote_score=F('vote_score') - 1)
                    KarmaTransaction.log_karma_change(
                        user=comment.author,
                        delta=-1,
                        reason='comment_upvote_removed',
                        comment=comment
                    )
                else:
                    Comment.objects.filter(pk=pk).update(vote_score=F('vote_score') + 1)
                    KarmaTransaction.log_karma_change(
                        user=comment.author,
                        delta=1,
                        reason='comment_downvote_removed',
                        comment=comment
                    )
                
                comment.refresh_from_db()
                return Response({'message': 'Vote removed', 'vote_score': comment.vote_score})
            else:
                # Different vote - update it (swing of 2)
                old_vote_type = existing_vote.vote_type
                existing_vote.vote_type = vote_type
                existing_vote.save()
                
                if vote_type == 'up':  # Changed from down to up
                    Comment.objects.filter(pk=pk).update(vote_score=F('vote_score') + 2)
                    KarmaTransaction.log_karma_change(
                        user=comment.author,
                        delta=2,
                        reason='comment_upvote',
                        comment=comment
                    )
                else:  # Changed from up to down
                    Comment.objects.filter(pk=pk).update(vote_score=F('vote_score') - 2)
                    KarmaTransaction.log_karma_change(
                        user=comment.author,
                        delta=-2,
                        reason='comment_downvote',
                        comment=comment
                    )
                
                comment.refresh_from_db()
                return Response({'message': 'Vote updated', 'vote_score': comment.vote_score})
        else:
            # New vote - create with atomic update
            CommentVote.objects.create(user=request.user, comment=comment, vote_type=vote_type)
            
            if vote_type == 'up':
                Comment.objects.filter(pk=pk).update(vote_score=F('vote_score') + 1)
                KarmaTransaction.log_karma_change(
                    user=comment.author,
                    delta=1,
                    reason='comment_upvote',
                    comment=comment
                )
            else:
                Comment.objects.filter(pk=pk).update(vote_score=F('vote_score') - 1)
                KarmaTransaction.log_karma_change(
                    user=comment.author,
                    delta=-1,
                    reason='comment_downvote',
                    comment=comment
                )
            
            comment.refresh_from_db()
            return Response({'message': 'Vote recorded', 'vote_score': comment.vote_score})


class PostCommentsView(generics.ListAPIView):
    """
    Get all top-level comments for a specific post.
    Uses prefetch_related to solve N+1 problem - loading 50 nested comments
    should NOT trigger 50 SQL queries.
    """
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        sort = self.request.query_params.get('sort', 'best')
        
        queryset = Comment.objects.filter(
            post_id=post_id,
            parent__isnull=True,
            is_deleted=False
        ).select_related('author')
        
        if sort == 'best':
            queryset = queryset.order_by('-vote_score', '-created_at')
        elif sort == 'new':
            queryset = queryset.order_by('-created_at')
        elif sort == 'old':
            queryset = queryset.order_by('created_at')
        
        # Apply N+1 optimization - prefetch all nested replies in one query
        queryset = get_prefetched_comments_queryset(queryset)
        
        return queryset
