from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q, F
from .models import Post, PostVote
from .serializers import (
    PostSerializer,
    PostCreateSerializer,
    PostListSerializer,
    VoteSerializer,
)


class PostListCreateView(generics.ListCreateAPIView):
    """List all posts or create a new post."""
    
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'vote_score', 'comment_count']
    ordering = ['-created_at']
    search_fields = ['title', 'content']
    
    def get_queryset(self):
        queryset = Post.objects.select_related('author', 'community')
        
        # Filter by community
        community_slug = self.request.query_params.get('community')
        if community_slug:
            queryset = queryset.filter(community__slug=community_slug)
        
        # Filter by author
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        
        # Sort option
        sort = self.request.query_params.get('sort', 'new')
        if sort == 'hot':
            # Simple hot algorithm: score weighted by recency
            queryset = queryset.order_by('-vote_score', '-created_at')
        elif sort == 'top':
            queryset = queryset.order_by('-vote_score')
        else:  # 'new'
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a post."""
    
    queryset = Post.objects.select_related('author', 'community')
    serializer_class = PostSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own posts.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own posts.")
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def vote_post(request, pk):
    """
    Upvote or downvote a post with ATOMIC transaction to prevent race conditions.
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
            # Lock the post row to prevent concurrent modifications
            post = Post.objects.select_for_update().get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Try to get existing vote with lock
        existing_vote = PostVote.objects.select_for_update().filter(
            user=request.user, 
            post=post
        ).first()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Same vote - remove it (toggle off)
                old_vote_type = existing_vote.vote_type
                existing_vote.delete()
                
                # Update vote score atomically
                if old_vote_type == 'up':
                    Post.objects.filter(pk=pk).update(vote_score=F('vote_score') - 1)
                    # Log karma transaction
                    KarmaTransaction.log_karma_change(
                        user=post.author,
                        delta=-1,
                        reason='post_upvote_removed',
                        post=post
                    )
                else:
                    Post.objects.filter(pk=pk).update(vote_score=F('vote_score') + 1)
                    KarmaTransaction.log_karma_change(
                        user=post.author,
                        delta=1,
                        reason='post_downvote_removed',
                        post=post
                    )
                
                post.refresh_from_db()
                return Response({'message': 'Vote removed', 'vote_score': post.vote_score})
            else:
                # Different vote - update it (swing of 2: remove old + add new)
                old_vote_type = existing_vote.vote_type
                existing_vote.vote_type = vote_type
                existing_vote.save()
                
                if vote_type == 'up':  # Changed from down to up
                    Post.objects.filter(pk=pk).update(vote_score=F('vote_score') + 2)
                    KarmaTransaction.log_karma_change(
                        user=post.author,
                        delta=2,  # +1 remove downvote, +1 add upvote
                        reason='post_upvote',
                        post=post
                    )
                else:  # Changed from up to down
                    Post.objects.filter(pk=pk).update(vote_score=F('vote_score') - 2)
                    KarmaTransaction.log_karma_change(
                        user=post.author,
                        delta=-2,  # -1 remove upvote, -1 add downvote
                        reason='post_downvote',
                        post=post
                    )
                
                post.refresh_from_db()
                return Response({'message': 'Vote updated', 'vote_score': post.vote_score})
        else:
            # New vote - create with atomic update
            PostVote.objects.create(user=request.user, post=post, vote_type=vote_type)
            
            if vote_type == 'up':
                Post.objects.filter(pk=pk).update(vote_score=F('vote_score') + 1)
                KarmaTransaction.log_karma_change(
                    user=post.author,
                    delta=1,
                    reason='post_upvote',
                    post=post
                )
            else:
                Post.objects.filter(pk=pk).update(vote_score=F('vote_score') - 1)
                KarmaTransaction.log_karma_change(
                    user=post.author,
                    delta=-1,
                    reason='post_downvote',
                    post=post
                )
            
            post.refresh_from_db()
            return Response({'message': 'Vote recorded', 'vote_score': post.vote_score})


class UserPostsView(generics.ListAPIView):
    """List all posts by a specific user."""
    
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        return Post.objects.filter(author__username=username).select_related('author', 'community')
