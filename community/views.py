from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    SocialPost, Comment, Challenge, GroupWorkout, 
    UserBadge, ProgressEntry, Achievement, ChallengeParticipation
)

# Create your views here.

@login_required
def community_home(request):
    challenges = Challenge.objects.filter(is_active=True).order_by('-start_date')
    recent_posts = SocialPost.objects.all().order_by('-created_at')[:5]
    upcoming_workouts = GroupWorkout.objects.filter(date_time__gte=timezone.now()).order_by('date_time')
    
    return render(request, 'community/home.html', {
        'challenges': challenges,
        'recent_posts': recent_posts,
        'upcoming_workouts': upcoming_workouts,
    })

@login_required
def challenges(request):
    active_challenges = Challenge.objects.filter(is_active=True).order_by('-start_date')
    past_challenges = Challenge.objects.filter(is_active=False).order_by('-end_date')
    
    return render(request, 'community/challenges.html', {
        'active_challenges': active_challenges,
        'past_challenges': past_challenges,
    })

@login_required
def challenge_detail(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    participation = ChallengeParticipation.objects.filter(
        user=request.user,
        challenge=challenge
    ).first()
    
    return render(request, 'community/challenge_detail.html', {
        'challenge': challenge,
        'participation': participation,
    })

@login_required
def social_feed(request):
    posts = SocialPost.objects.all().order_by('-created_at')
    return render(request, 'community/social_feed.html', {
        'posts': posts,
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if content:
            SocialPost.objects.create(
                content=content,
                image=image,
                user=request.user
            )
            messages.success(request, 'Post created successfully!')
            return redirect('community:social_feed')
        else:
            messages.error(request, 'Please enter some content.')
    return render(request, 'community/create_post.html')

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(SocialPost, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                content=content,
                post=post,
                user=request.user
            )
            messages.success(request, 'Comment added successfully!')
            return redirect('community:post_detail', post_id=post.id)
        else:
            messages.error(request, 'Please enter a comment.')
    
    comments = post.comments.all().order_by('-created_at')
    return render(request, 'community/post_detail.html', {
        'post': post,
        'comments': comments,
    })

@login_required
def group_workouts(request):
    upcoming_workouts = GroupWorkout.objects.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')
    past_workouts = GroupWorkout.objects.filter(
        date_time__lt=timezone.now()
    ).order_by('-date_time')
    
    return render(request, 'community/group_workouts.html', {
        'upcoming_workouts': upcoming_workouts,
        'past_workouts': past_workouts,
    })

@login_required
def workout_detail(request, workout_id):
    workout = get_object_or_404(GroupWorkout, id=workout_id)
    is_participant = workout.participants.filter(id=request.user.id).exists()
    
    return render(request, 'community/workout_detail.html', {
        'workout': workout,
        'is_participant': is_participant,
    })

@login_required
def create_workout(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        workout_type = request.POST.get('workout_type')
        date_time = request.POST.get('date_time')
        duration = request.POST.get('duration')
        max_participants = request.POST.get('max_participants')
        location = request.POST.get('location')
        meeting_link = request.POST.get('meeting_link')

        if all([title, description, workout_type, date_time, duration, max_participants]):
            workout = GroupWorkout.objects.create(
                title=title,
                description=description,
                workout_type=workout_type,
                date_time=date_time,
                duration=duration,
                max_participants=max_participants,
                location=location,
                meeting_link=meeting_link,
                created_by=request.user
            )
            messages.success(request, 'Group workout created successfully!')
            return redirect('community:workout_detail', workout_id=workout.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'community/create_workout.html')

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = SocialPost.objects.filter(user=user).order_by('-created_at')
    achievements = Achievement.objects.filter(user=user).order_by('-date_achieved')
    badges = UserBadge.objects.filter(user=user).order_by('-date_earned')
    progress_entries = ProgressEntry.objects.filter(user=user).order_by('-date')
    
    return render(request, 'community/user_profile.html', {
        'profile_user': user,
        'posts': posts,
        'achievements': achievements,
        'badges': badges,
        'progress_entries': progress_entries,
    })
