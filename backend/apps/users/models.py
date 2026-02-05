from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    """Custom user model with additional fields for community features."""
    
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    # NOTE: This karma field is for display/caching only. 
    # For 24h leaderboard, use get_karma_24h() which calculates from KarmaTransaction
    karma = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email is required for registration
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def get_karma_24h(self):
        """
        Calculate karma earned in the last 24 hours dynamically.
        This is used for the leaderboard - NOT stored as a simple integer.
        """
        from django.db.models import Sum
        yesterday = timezone.now() - timedelta(hours=24)
        
        result = KarmaTransaction.objects.filter(
            user=self,
            created_at__gte=yesterday
        ).aggregate(total=Sum('delta'))
        
        return result['total'] or 0
    
    def get_total_karma(self):
        """Calculate total karma from all transactions."""
        from django.db.models import Sum
        result = KarmaTransaction.objects.filter(user=self).aggregate(
            total=Sum('delta')
        )
        return result['total'] or 0
    
    def update_karma_cache(self):
        """Update the cached karma field from transactions."""
        self.karma = self.get_total_karma()
        self.save(update_fields=['karma'])


class KarmaTransaction(models.Model):
    """
    Immutable log of all karma changes.
    Used for dynamic 24h leaderboard calculations instead of storing
    daily karma as a simple integer field.
    """
    
    REASON_CHOICES = [
        ('post_upvote', 'Post Upvote'),
        ('post_downvote', 'Post Downvote'),
        ('post_upvote_removed', 'Post Upvote Removed'),
        ('post_downvote_removed', 'Post Downvote Removed'),
        ('comment_upvote', 'Comment Upvote'),
        ('comment_downvote', 'Comment Downvote'),
        ('comment_upvote_removed', 'Comment Upvote Removed'),
        ('comment_downvote_removed', 'Comment Downvote Removed'),
    ]
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='karma_transactions',
        db_index=True
    )
    delta = models.IntegerField(
        help_text="Change in karma: +1 for upvote, -1 for downvote"
    )
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    
    # Reference to what caused this karma change
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    comment = models.ForeignKey(
        'comments.Comment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Composite index for efficient 24h leaderboard queries
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.delta:+d} karma ({self.reason})"
    
    @classmethod
    def log_karma_change(cls, user, delta, reason, post=None, comment=None):
        """Create a karma transaction and update user's cached karma."""
        transaction = cls.objects.create(
            user=user,
            delta=delta,
            reason=reason,
            post=post,
            comment=comment
        )
        # Update cached karma field
        user.karma = models.F('karma') + delta
        user.save(update_fields=['karma'])
        return transaction
