from django.contrib import admin
from .models import Post, PostVote


class PostVoteInline(admin.TabularInline):
    model = PostVote
    extra = 0
    readonly_fields = ['user', 'vote_type', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'community', 'post_type', 'vote_score', 'comment_count', 'created_at']
    list_filter = ['post_type', 'is_pinned', 'is_locked', 'is_nsfw', 'community']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['vote_score', 'comment_count', 'created_at', 'updated_at']
    inlines = [PostVoteInline]


@admin.register(PostVote)
class PostVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['user__username', 'post__title']
