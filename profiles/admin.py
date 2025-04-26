from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'country', 'newsletter_subscription')
    list_filter = ('newsletter_subscription', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'city')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


admin.site.register(UserProfile, UserProfileAdmin)
