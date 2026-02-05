from django.contrib import admin
from .models import Community, CommunityMembership


class CommunityMembershipInline(admin.TabularInline):
    model = CommunityMembership
    extra = 0
    readonly_fields = ['joined_at']


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'creator', 'member_count', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['moderators']
    inlines = [CommunityMembershipInline]
