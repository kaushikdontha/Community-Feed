# 🔍 Technical Explainer

This document explains the key technical decisions and implementations in Community Feed.

---

## 📌 The Tree: Nested Comments

### Database Model

Nested comments are modeled using a **self-referential ForeignKey** (Adjacency List pattern):

```python
# backend/apps/comments/models.py

class Comment(models.Model):
    content = models.TextField(max_length=10000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    # Self-referential relationship for nesting
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,      # null = top-level comment
        blank=True,
        related_name='replies'
    )
    
    vote_score = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
```

**Why Adjacency List?**
- Simple to understand and implement
- Easy to add new replies (just set `parent_id`)
- Works well for Reddit-style trees (typically 3-5 levels deep)

### Avoiding N+1 Queries

Without optimization, fetching 50 comments would trigger **50+ SQL queries** (one for each comment's replies). We solve this with `prefetch_related`:

```python
# backend/apps/comments/views.py

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
        'votes',
        'replies__votes',
        'replies__replies__votes',
    )
```

**Result:** 50 nested comments load in **~6 queries** instead of 50+.

---

## 📌 The Math: 24-Hour Leaderboard

### The Constraint

Daily karma is **NOT** stored as a simple integer field. It's calculated **dynamically** from an immutable transaction log.

### Karma Transaction Model

```python
# backend/apps/users/models.py

class KarmaTransaction(models.Model):
    """Immutable log of all karma changes."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delta = models.IntegerField()  # +1 or -1
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),  # Optimizes 24h queries
        ]
```

### The Leaderboard Query

```python
# backend/apps/users/views.py

@api_view(['GET'])
def leaderboard_24h(request):
    yesterday = timezone.now() - timedelta(hours=24)
    limit = int(request.query_params.get('limit', 10))
    limit = min(limit, 100)  # Cap at 100
    
    # Aggregate karma from transactions in the last 24 hours
    leaderboard = KarmaTransaction.objects.filter(
        created_at__gte=yesterday
    ).values(
        'user__id',
        'user__username',
        'user__avatar',
    ).annotate(
        karma_24h=Sum('delta')
    ).order_by('-karma_24h')[:limit]
    
    return Response({'leaderboard': leaderboard})
```

### Generated SQL

```sql
SELECT 
    users_user.id,
    users_user.username,
    users_user.avatar,
    SUM(users_karmatransaction.delta) AS karma_24h
FROM users_karmatransaction
INNER JOIN users_user ON (users_karmatransaction.user_id = users_user.id)
WHERE users_karmatransaction.created_at >= '2026-02-04T10:47:21+05:30'
GROUP BY users_user.id, users_user.username, users_user.avatar
ORDER BY karma_24h DESC
LIMIT 10;
```

**Why this approach?**
- Accurately reflects karma in *exactly* the last 24 hours (rolling window)
- Prevents gaming - can't manipulate a stored field
- Transaction history enables auditing and analysis

---

## 📌 The AI Audit: Bug Fix Example

### The Bug: PostVote Model Field Mismatch

When creating the seed data script, the AI assumed PostVote used a numeric `value` field:

```python
# ❌ BUGGY CODE - AI's initial assumption
vote, created = PostVote.objects.get_or_create(
    post=post,
    user=user,
    defaults={"value": 1}  # Wrong! Field doesn't exist
)
```

**Error:**
```
FieldError: Invalid field name(s) for model PostVote: 'value'
```

### The Investigation

Inspecting the actual model revealed it uses `vote_type` with choices `'up'` / `'down'`:

```python
# backend/apps/posts/models.py

class PostVote(models.Model):
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)  # Not 'value'!
```

### The Fix

```python
# ✅ FIXED CODE
from django.db.models import F

vote, created = PostVote.objects.get_or_create(
    post=post,
    user=user,
    defaults={"vote_type": "up"}  # Correct field name
)
if created:
    # Also need to update the denormalized vote_score
    Post.objects.filter(pk=post.pk).update(vote_score=F('vote_score') + 1)
```

### Lessons Learned

1. **Don't assume model structure** - Always check the actual model definition
2. **Consider side effects** - Creating a vote also requires updating the post's `vote_score`
3. **Use atomic operations** - `F()` expression prevents race conditions when multiple users vote

---

## 🔗 Live Demo

- **Hosted App:** [Coming Soon - Railway/Vercel deployment]
- **API Docs:** http://localhost:8000/api/

---

## 📚 Additional Resources

- [Django Prefetch Documentation](https://docs.djangoproject.com/en/5.0/ref/models/querysets/#prefetch-related)
- [Django F() Expressions](https://docs.djangoproject.com/en/5.0/ref/models/expressions/#f-expressions)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
