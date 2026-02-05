"""
Seed script to populate the database with test data.
Run with: python manage.py shell < seed_data.py
Or: python manage.py runscript seed_data (if django-extensions is installed)
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_feed.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.users.models import User
from apps.communities.models import Community, CommunityMembership
from apps.posts.models import Post, PostVote
from apps.comments.models import Comment
from django.db.models import F

def create_seed_data():
    print("🌱 Creating seed data...")
    
    # Create 6 test users
    users_data = [
        {"username": "alice", "email": "alice@example.com", "password": "testpass123"},
        {"username": "bob", "email": "bob@example.com", "password": "testpass123"},
        {"username": "charlie", "email": "charlie@example.com", "password": "testpass123"},
        {"username": "diana", "email": "diana@example.com", "password": "testpass123"},
        {"username": "eve", "email": "eve@example.com", "password": "testpass123"},
        {"username": "frank", "email": "frank@example.com", "password": "testpass123"},
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data["username"],
            defaults={"email": user_data["email"]}
        )
        if created:
            user.set_password(user_data["password"])
            user.save()
            print(f"  ✅ Created user: {user.username}")
        else:
            print(f"  ℹ️ User already exists: {user.username}")
        users.append(user)
    
    alice, bob, charlie, diana, eve, frank = users
    
    # Create General community
    general, created = Community.objects.get_or_create(
        name="General",
        defaults={
            "slug": "general",
            "description": "The main community for general discussions. Share anything interesting!",
            "creator": alice,
        }
    )
    if created:
        print(f"  ✅ Created community: {general.name}")
    else:
        print(f"  ℹ️ Community already exists: {general.name}")
    
    # Add all users as members of General community
    for user in users:
        membership, created = CommunityMembership.objects.get_or_create(
            user=user,
            community=general
        )
        if created:
            print(f"  ✅ Added {user.username} to {general.name}")
    
    # Create example posts
    posts_data = [
        {
            "title": "Welcome to our Community Feed!",
            "content": "Hey everyone! 👋 This is the first post in our new community platform. Feel free to introduce yourself and share what you're working on. Looking forward to great discussions here!",
            "author": alice,
        },
        {
            "title": "Tips for writing great posts",
            "content": "Here are some tips for creating engaging content:\n\n1. **Be clear and concise** - Get to the point quickly\n2. **Use formatting** - Break up text with headers and lists\n3. **Add value** - Share something useful or interesting\n4. **Engage with comments** - Reply to people who respond\n\nWhat tips would you add?",
            "author": bob,
        },
        {
            "title": "Just discovered an amazing programming trick!",
            "content": "I just learned about list comprehensions with conditionals in Python and it blew my mind! 🤯\n\n```python\n# Old way\nresult = []\nfor x in range(10):\n    if x % 2 == 0:\n        result.append(x * 2)\n\n# New way\nresult = [x * 2 for x in range(10) if x % 2 == 0]\n```\n\nSo much cleaner!",
            "author": charlie,
        },
        {
            "title": "Weekend project ideas?",
            "content": "I've got some free time this weekend and want to build something fun. Any project ideas?\n\nI'm comfortable with:\n- Python\n- JavaScript/React\n- Some basic machine learning\n\nLooking for something I can finish in a day or two!",
            "author": diana,
        },
        {
            "title": "The importance of code reviews",
            "content": "Just wanted to share my experience with code reviews.\n\nBefore: I thought they were just about finding bugs.\n\nAfter: I realized they're about:\n- Knowledge sharing\n- Maintaining code quality\n- Learning from teammates\n- Building team culture\n\nCode reviews have made me a much better developer. What's your experience?",
            "author": eve,
        },
        {
            "title": "Hot take: Tabs vs Spaces doesn't matter",
            "content": "I know this is controversial, but hear me out... 😅\n\nAs long as your team is consistent, it really doesn't matter whether you use tabs or spaces. What matters is:\n\n1. Having a linter configured\n2. Auto-formatting on save\n3. Everyone using the same settings\n\nChange my mind! ⬇️",
            "author": frank,
        },
    ]
    
    posts = []
    for post_data in posts_data:
        post, created = Post.objects.get_or_create(
            title=post_data["title"],
            defaults={
                "content": post_data["content"],
                "author": post_data["author"],
                "community": general,
            }
        )
        if created:
            print(f"  ✅ Created post: {post.title[:40]}...")
        else:
            print(f"  ℹ️ Post already exists: {post.title[:40]}...")
        posts.append(post)
    
    # Add some votes to posts
    vote_data = [
        (posts[0], [alice, bob, charlie, diana, eve, frank], []),  # Welcome post - all upvotes
        (posts[1], [alice, charlie, eve], []),  # Tips post
        (posts[2], [bob, diana, frank, alice], []),  # Python trick
        (posts[3], [alice, bob, charlie], [eve]),  # Weekend project
        (posts[4], [diana, eve, frank, bob], []),  # Code reviews
        (posts[5], [alice, diana], [bob, charlie]),  # Tabs vs spaces - controversial!
    ]
    
    for post, upvoters, downvoters in vote_data:
        for user in upvoters:
            vote, created = PostVote.objects.get_or_create(
                post=post,
                user=user,
                defaults={"vote_type": "up"}
            )
            if created:
                # Update the post's vote_score
                Post.objects.filter(pk=post.pk).update(vote_score=F('vote_score') + 1)
        for user in downvoters:
            vote, created = PostVote.objects.get_or_create(
                post=post,
                user=user,
                defaults={"vote_type": "down"}
            )
            if created:
                # Update the post's vote_score
                Post.objects.filter(pk=post.pk).update(vote_score=F('vote_score') - 1)
    
    print("  ✅ Added votes to posts")
    
    # Add some comments
    comments_data = [
        (posts[0], bob, "Welcome! Excited to be here! 🎉"),
        (posts[0], charlie, "Great to see this community growing!"),
        (posts[1], alice, "Great tips! I'd add: proofread before posting."),
        (posts[2], frank, "Wait until you discover generators! Even more mind-blowing."),
        (posts[3], bob, "How about a CLI tool? Always useful and you learn a lot."),
        (posts[3], eve, "Maybe a personal dashboard? I built one last month and loved it."),
        (posts[4], alice, "100% agree! Code reviews have taught me so much."),
        (posts[5], charlie, "SPACES FOREVER! 🚀"),
        (posts[5], eve, "Tabs for accessibility reasons - screen readers work better with them."),
    ]
    
    for post, author, content in comments_data:
        comment, created = Comment.objects.get_or_create(
            post=post,
            author=author,
            content=content
        )
        if created:
            print(f"  ✅ Added comment by {author.username}")
    
    print("\n✨ Seed data creation complete!")
    print(f"   - Users: {User.objects.count()}")
    print(f"   - Communities: {Community.objects.count()}")
    print(f"   - Posts: {Post.objects.count()}")
    print(f"   - Comments: {Comment.objects.count()}")

if __name__ == "__main__":
    create_seed_data()
