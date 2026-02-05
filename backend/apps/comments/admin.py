from django.contrib import admin
from .models import Comment, CommentVote


class CommentVoteInline(admin.TabularInline):
    model = CommentVote
    extra = 0
    readonly_fields = ['user', 'vote_type', 'created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'parent', 'vote_score', 'is_deleted', 'created_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['vote_score', 'created_at', 'updated_at']
    inlines = [CommentVoteInline]


@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
