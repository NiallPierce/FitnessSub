from django.contrib import admin
from .models import (
    Achievement, Badge, UserBadge, Challenge, ChallengeParticipation,
    ProgressEntry, SocialPost, Comment, GroupWorkout
)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'date_achieved', 'points')
    list_filter = ('date_achieved',)
    search_fields = ('user__username', 'title')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'required_points')
    list_filter = ('badge_type',)
    search_fields = ('name', 'description')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'date_earned')
    list_filter = ('date_earned',)
    search_fields = ('user__username', 'badge__name')


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')


@admin.register(ChallengeParticipation)
class ChallengeParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'joined_date', 'completed')
    list_filter = ('completed', 'joined_date')
    search_fields = ('user__username', 'challenge__title')


@admin.register(ProgressEntry)
class ProgressEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry_type', 'title', 'date')
    list_filter = ('entry_type', 'date')
    search_fields = ('user__username', 'title', 'description')


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'content')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')


@admin.register(GroupWorkout)
class GroupWorkoutAdmin(admin.ModelAdmin):
    list_display = ('title', 'workout_type', 'date_time', 'created_by')
    list_filter = ('workout_type', 'date_time')
    search_fields = ('title', 'description', 'created_by__username')
