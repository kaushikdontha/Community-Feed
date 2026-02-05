# Technical Explainer

This document explains the key technical features of Community Feed.

---

## Nested Comments

Comments support replies to create threaded discussions, similar to Reddit.

### How It Works

Each comment has a `parent` field that points to another comment:

```python
class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    
    # Points to parent comment (null = top-level)
    parent = models.ForeignKey('self', null=True, related_name='replies')
```

- **Top-level comments** have `parent = null`
- **Replies** have `parent = the comment they're replying to`

This creates a tree structure where each comment can have many replies.

---

## 24-Hour Karma Leaderboard

The leaderboard shows users who earned the most karma in the last 24 hours.

### How It Works

Instead of storing "daily karma" as a number, we log every karma change:

```python
class KarmaTransaction(models.Model):
    user = models.ForeignKey(User)
    delta = models.IntegerField()  # +1 for upvote, -1 for downvote
    created_at = models.DateTimeField(auto_now_add=True)
```

When someone upvotes your post:
1. A `KarmaTransaction` is created with `delta = +1`
2. Your total karma increases

### Getting the Leaderboard

We sum up all karma changes from the last 24 hours:

```python
yesterday = timezone.now() - timedelta(hours=24)

leaderboard = KarmaTransaction.objects.filter(
    created_at__gte=yesterday
).values('user__username').annotate(
    karma_24h=Sum('delta')
).order_by('-karma_24h')[:10]
```

This gives us the top 10 users by karma earned in the last 24 hours.

**Benefits:**
- Accurate rolling 24-hour window
- Can't be cheated by manipulating stored values
- Full history for analysis

---

## Voting System

Posts and comments can be upvoted or downvoted.

### How It Works

```python
class PostVote(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    vote_type = models.CharField(choices=[('up', 'Upvote'), ('down', 'Downvote')])
    
    class Meta:
        unique_together = ['user', 'post']  # One vote per user per post
```

The `unique_together` constraint prevents users from voting multiple times on the same post.

---

## Authentication

We use JWT (JSON Web Tokens) for secure authentication.

### Login Flow

1. User sends username/password to `/api/token/`
2. Server validates and returns access + refresh tokens
3. Frontend stores tokens and includes them in API requests
4. Access token expires in 1 hour, refresh token in 7 days

```javascript
// Frontend sends token with every request
headers: { 'Authorization': 'Bearer ' + accessToken }
```

---

## Database

- **Development:** SQLite (simple, no setup)
- **Production:** PostgreSQL (reliable, scalable)

The app automatically detects which database to use based on the `DATABASE_URL` environment variable.
