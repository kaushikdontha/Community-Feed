from django.db import models
from django.conf import settings


class Community(models.Model):
    """Subreddit-like community model."""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True)
    rules = models.TextField(blank=True)
    banner = models.ImageField(upload_to='community_banners/', null=True, blank=True)
    icon = models.ImageField(upload_to='community_icons/', null=True, blank=True)
    
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_communities'
    )
    moderators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='moderated_communities',
        blank=True
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CommunityMembership',
        related_name='joined_communities'
    )
    
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Communities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"c/{self.name}"
    
    @property
    def member_count(self):
        return self.members.count()


class CommunityMembership(models.Model):
    """Through model for community membership."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'community']
    
    def __str__(self):
        return f"{self.user.username} in {self.community.name}"
