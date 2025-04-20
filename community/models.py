from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
import os

def achievement_image_path(instance, filename):
    return f'achievements/{instance.id}/{filename}'

def badge_image_path(instance, filename):
    return f'badges/{instance.id}/{filename}'

class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to=achievement_image_path, null=True, blank=True)
    date_achieved = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s achievement: {self.title}"

class Badge(models.Model):
    BADGE_TYPES = [
        ('workout', 'Workout'),
        ('nutrition', 'Nutrition'),
        ('community', 'Community'),
        ('streak', 'Streak'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    image = models.ImageField(upload_to=badge_image_path)
    required_points = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class Challenge(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    points = models.IntegerField(default=0)
    participants = models.ManyToManyField(User, through='ChallengeParticipation')
    is_active = models.BooleanField(default=True)
    requirements = models.ManyToManyField('ChallengeRequirement', related_name='challenges')
    rewards = models.ManyToManyField('ChallengeReward', related_name='challenges')

    def __str__(self):
        return self.title

class ChallengeRequirement(models.Model):
    description = models.TextField()
    is_mandatory = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Requirement: {self.description[:50]}..."

class ChallengeReward(models.Model):
    description = models.TextField()
    points_value = models.IntegerField(default=0)
    badge = models.ForeignKey('Badge', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Reward: {self.description[:50]}..."

class ChallengeParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"

class ProgressEntry(models.Model):
    ENTRY_TYPES = [
        ('workout', 'Workout'),
        ('nutrition', 'Nutrition'),
        ('measurement', 'Measurement'),
        ('goal', 'Goal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_entries')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='progress_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s {self.entry_type} entry: {self.title}"

class SocialPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_posts')
    content = models.TextField()
    image = models.ImageField(upload_to='social_posts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"Post by {self.user.username}"

class Comment(models.Model):
    post = models.ForeignKey(SocialPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"

class GroupWorkout(models.Model):
    WORKOUT_TYPES = [
        ('virtual', 'Virtual'),
        ('local', 'Local'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPES)
    date_time = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    max_participants = models.IntegerField()
    participants = models.ManyToManyField(User, related_name='group_workouts')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workouts')
    location = models.CharField(max_length=255, null=True, blank=True)
    meeting_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title 