from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, KarmaTransaction


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'karma', 'get_karma_24h_display', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('bio', 'avatar', 'karma')}),
    )
    
    readonly_fields = ['karma', 'created_at', 'updated_at']
    
    def get_karma_24h_display(self, obj):
        return obj.get_karma_24h()
    get_karma_24h_display.short_description = '24h Karma'


@admin.register(KarmaTransaction)
class KarmaTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'delta', 'reason', 'post', 'comment', 'created_at']
    list_filter = ['reason', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['user', 'delta', 'reason', 'post', 'comment', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        # Transactions are immutable - can't be added manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Transactions are immutable - can't be changed
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Transactions are immutable - can't be deleted
        return False
