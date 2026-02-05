from django.db import models
from django.conf import settings


class Comment(models.Model):
    """
    Threaded comment model with voting.
    
    N+1 OPTIMIZATION:
    Comments are fetched using prefetch_related for nested replies
    to avoid triggering 50 queries for 50 comments.
    """
    
    content = models.TextField(max_length=10000)
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    vote_score = models.IntegerField(default=0, db_index=True)
    is_deleted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'parent', '-vote_score']),
            models.Index(fields=['post', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title[:30]}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.post.update_comment_count()
    
    def delete(self, *args, **kwargs):
        post = self.post
        super().delete(*args, **kwargs)
        post.update_comment_count()
    
    @property
    def reply_count(self):
        return self.replies.count()


class CommentVote(models.Model):
    """
    Vote model for comments (upvote/downvote).
    
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
        related_name='comment_votes'
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # This unique constraint prevents double-voting at the database level
        unique_together = ['user', 'comment']
    
    def __str__(self):
        return f"{self.user.username} {self.vote_type}voted comment"
    
    # NOTE: We do NOT override save/delete to update vote_score here
    # Vote score updates are handled atomically in the view layer using F() expressions
    # This prevents race conditions when multiple users vote simultaneously
