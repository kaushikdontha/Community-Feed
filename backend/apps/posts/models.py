from django.db import models
from django.conf import settings


class Post(models.Model):
    """Reddit-style post model with voting."""
    
    POST_TYPE_CHOICES = [
        ('text', 'Text'),
        ('link', 'Link'),
        ('image', 'Image'),
    ]
    
    title = models.CharField(max_length=300)
    content = models.TextField(blank=True)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='text')
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    
    vote_score = models.IntegerField(default=0, db_index=True)
    comment_count = models.IntegerField(default=0)
    
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_nsfw = models.BooleanField(default=False)
    is_spoiler = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['community', '-created_at']),
            models.Index(fields=['-vote_score', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def update_comment_count(self):
        """Update the comment count."""
        from django.db.models import F
        Post.objects.filter(pk=self.pk).update(
            comment_count=self.comments.count()
        )


class PostVote(models.Model):
    """
    Vote model for posts (upvote/downvote).
    
    CONCURRENCY PROTECTION:
    - unique_together constraint prevents double-voting at the DB level
    - Vote score updates use atomic F() expressions in views
    - select_for_update is used to lock rows during voting
    """
    
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_votes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # This unique constraint prevents double-voting at the database level
        unique_together = ['user', 'post']
    
    def __str__(self):
        return f"{self.user.username} {self.vote_type}voted {self.post.title[:30]}"
    
    # NOTE: We do NOT override save/delete to update vote_score here
    # Vote score updates are handled atomically in the view layer using F() expressions
    # This prevents race conditions when multiple users vote simultaneously
