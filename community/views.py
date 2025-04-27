from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    SocialPost, Comment, Challenge, GroupWorkout,
    UserBadge, ProgressEntry, Achievement, ChallengeParticipation,
    ChallengeRequirement, ChallengeReward, Badge
)
from .forms import CommentForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# Create your views here.


@login_required
def community_home(request):
    challenges = Challenge.objects.filter(
        is_active=True
    ).order_by('-start_date')
    recent_posts = SocialPost.objects.all().order_by('-created_at')[:5]
    upcoming_workouts = GroupWorkout.objects.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')

    return render(
        request,
        'community/home.html',
        {
            'challenges': challenges,
            'recent_posts': recent_posts,
            'upcoming_workouts': upcoming_workouts,
        }
    )


@login_required
def challenges(request):
    # Get all active challenges
    active_challenges = Challenge.objects.filter(
        is_active=True
    ).order_by('-start_date')

    # Get user's active challenges
    user_challenges = Challenge.objects.filter(
        challengeparticipation__user=request.user,
        challengeparticipation__completed=False
    ).order_by('-start_date')

    # Get completed challenges
    completed_challenges = Challenge.objects.filter(
        challengeparticipation__user=request.user,
        challengeparticipation__completed=True
    ).order_by('-start_date')

    # Check if there's already an active C25K challenge
    c25k_challenge = Challenge.objects.filter(
        title="Couch to 5K Challenge",
        is_active=True
    ).first()

    # If no active C25K challenge exists, create one
    if not c25k_challenge:
        c25k_challenge = Challenge.objects.create(
            title="Couch to 5K Challenge",
            description=(
                "Transform your fitness journey with our 9-week Couch to 5K "
                "program!\n\n"
                "This beginner-friendly challenge is designed to take you "
                "from no running experience to completing a 5K run. Perfect "
                "for those starting their fitness journey or looking to get "
                "back into running.\n\n"
                "Program Highlights:\n"
                "• 3 structured workouts per week\n"
                "• Gradual progression from walking to running\n"
                "• Supportive community of fellow runners\n"
                "• Weekly progress tracking\n"
                "• Achievement badges for reaching milestones\n"
                "• Expert guidance and tips\n\n"
                "Whether you're a complete beginner or returning to running, "
                "this program will help you build endurance, improve your "
                "fitness, and achieve your 5K goal in just 9 weeks!"
            ),
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(weeks=9),
            points=500,
            is_active=True
        )

        # Create requirements
        requirements = [
            "Complete 3 workouts per week",
            "Follow the weekly training schedule",
            "Track your progress in the app",
            "Share your journey in the community (optional)",
            "Complete the final 5K run"
        ]

        for i, req in enumerate(requirements):
            requirement = ChallengeRequirement.objects.create(
                description=req,
                is_mandatory=(i != 3),  # Only sharing is optional
                order=i
            )
            c25k_challenge.requirements.add(requirement)

        # Create rewards
        rewards = [
            {
                "description": "Complete Week 1",
                "points_value": 50,
                "badge": None
            },
            {
                "description": "Complete Week 4",
                "points_value": 100,
                "badge": None
            },
            {
                "description": "Complete the 5K Challenge",
                "points_value": 350,
                "badge": Badge.objects.get_or_create(
                    name="5K Runner",
                    defaults={
                        'description': 'Completed the Couch to 5K Challenge',
                        'badge_type': 'achievement',
                        'required_points': 500
                    }
                )[0]
            }
        ]

        for reward_data in rewards:
            reward = ChallengeReward.objects.create(
                description=reward_data["description"],
                points_value=reward_data["points_value"],
                badge=reward_data["badge"]
            )
            c25k_challenge.rewards.add(reward)

    return render(
        request,
        'community/challenges.html',
        {
            'active_challenges': active_challenges,
            'user_challenges': user_challenges,
            'completed_challenges': completed_challenges,
        }
    )


@login_required
def challenge_detail(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    participation = ChallengeParticipation.objects.filter(
        user=request.user,
        challenge=challenge
    ).first()

    return render(
        request,
        'community/challenge_detail.html',
        {
            'challenge': challenge,
            'participation': participation,
        }
    )


@login_required
def social_feed(request):
    posts = SocialPost.objects.all().order_by('-created_at')
    return render(
        request,
        'community/social_feed.html',
        {'posts': posts}
    )


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
            messages.success(
                request,
                'Post created successfully!'
            )
            return redirect('community:social_feed')
        else:
            messages.error(
                request,
                'Please enter some content.'
            )
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
            messages.success(
                request,
                'Comment added successfully!'
            )
            return redirect('community:post_detail', post_id=post.id)
        else:
            messages.error(
                request,
                'Please enter a comment.'
            )

    comments = post.comments.all().order_by('-created_at')
    return render(
        request,
        'community/post_detail.html',
        {
            'post': post,
            'comments': comments,
        }
    )


@login_required
def group_workouts(request):
    upcoming_workouts = GroupWorkout.objects.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')
    past_workouts = GroupWorkout.objects.filter(
        date_time__lt=timezone.now()
    ).order_by('-date_time')

    return render(
        request,
        'community/group_workouts.html',
        {
            'upcoming_workouts': upcoming_workouts,
            'past_workouts': past_workouts,
        }
    )


@login_required
def workout_detail(request, workout_id):
    workout = get_object_or_404(GroupWorkout, id=workout_id)
    is_participant = workout.participants.filter(
        id=request.user.id
    ).exists()

    return render(
        request,
        'community/workout_detail.html',
        {
            'workout': workout,
            'is_participant': is_participant,
        }
    )


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

        if all([
            title,
            description,
            workout_type,
            date_time,
            duration,
            max_participants
        ]):
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
            messages.success(
                request,
                'Group workout created successfully!'
            )
            return redirect(
                'community:workout_detail',
                workout_id=workout.id
            )
        else:
            messages.error(
                request,
                'Please fill in all required fields.'
            )

    return render(request, 'community/create_workout.html')


@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = SocialPost.objects.filter(
        user=user
    ).order_by('-created_at')
    achievements = Achievement.objects.filter(
        user=user
    ).order_by('-date_achieved')
    badges = UserBadge.objects.filter(
        user=user
    ).order_by('-date_earned')
    progress_entries = ProgressEntry.objects.filter(
        user=user
    ).order_by('-date')

    return render(
        request,
        'community/user_profile.html',
        {
            'profile_user': user,
            'posts': posts,
            'achievements': achievements,
            'badges': badges,
            'progress_entries': progress_entries,
        }
    )


@login_required
def create_c25k_challenge(request):
    if request.method == 'POST':
        # Create the main challenge
        challenge = Challenge.objects.create(
            title="Couch to 5K Challenge",
            description="""
            Join our 9-week Couch to 5K program! This beginner-friendly
             challenge will help you go from no running experience to
             completing a 5K run.

            What to expect:
            - 3 workouts per week
            - Gradual progression from walking to running
            - Supportive community
            - Weekly progress tracking
            - Achievement badges for milestones
            """,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(weeks=9),
            points=500,
            is_active=True
        )

        # Create requirements
        requirements = [
            "Complete 3 workouts per week",
            "Follow the weekly training schedule",
            "Track your progress in the app",
            "Share your journey in the community (optional)",
            "Complete the final 5K run"
        ]

        for i, req in enumerate(requirements):
            ChallengeRequirement.objects.create(
                description=req,
                is_mandatory=(i != 3),  # Only sharing is optional
                order=i
            )

        # Add requirements to challenge
        challenge.requirements.add(*ChallengeRequirement.objects.all())

        # Create rewards
        rewards = [
            {
                "description": "Complete Week 1",
                "points_value": 50,
                "badge": None
            },
            {
                "description": "Complete Week 4",
                "points_value": 100,
                "badge": None
            },
            {
                "description": "Complete the 5K Challenge",
                "points_value": 350,
                "badge": Badge.objects.get_or_create(
                    name="5K Runner",
                    defaults={
                        'description': 'Completed the Couch to 5K Challenge',
                        'badge_type': 'achievement',
                        'required_points': 500
                    }
                )[0]
            }
        ]

        for reward_data in rewards:
            reward = ChallengeReward.objects.create(
                description=reward_data["description"],
                points_value=reward_data["points_value"],
                badge=reward_data["badge"]
            )
            challenge.rewards.add(reward)

        # Create weekly progress entries for tracking
        weeks = [
            "Week 1: 60s run, 90s walk x 8",
            "Week 2: 90s run, 2m walk x 8",
            "Week 3: 3m run, 3m walk x 3",
            "Week 4: 5m run, 3m walk x 3",
            "Week 5: 8m run, 5m walk x 2",
            "Week 6: 10m run, 3m walk x 2",
            "Week 7: 15m run continuous",
            "Week 8: 20m run continuous",
            "Week 9: 30m run (5K) continuous"
        ]

        for week_num, description in enumerate(weeks, 1):
            ProgressEntry.objects.create(
                user=request.user,
                entry_type='goal',
                title=f"C25K Week {week_num}",
                description=description,
                date=timezone.now() + timezone.timedelta(weeks=week_num - 1)
            )

        # Join the user to the challenge
        ChallengeParticipation.objects.create(
            user=request.user,
            challenge=challenge,
            completed=False
        )

        messages.success(
            request,
            'Couch to 5K challenge created! Start your first workout today.'
        )
        return redirect(
            'community:challenge_detail',
            challenge_id=challenge.id
        )

    return render(request, 'community/create_c25k.html')


@login_required
def update_c25k_progress(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    participation = get_object_or_404(
        ChallengeParticipation,
        user=request.user,
        challenge=challenge
    )

    if request.method == 'POST':
        week_number = int(request.POST.get('week_number'))
        completed = request.POST.get('completed') == 'true'

        progress_entry = ProgressEntry.objects.filter(
            user=request.user,
            entry_type='goal',
            title=f"C25K Week {week_number}"
        ).first()

        if progress_entry:
            progress_entry.value = 100 if completed else 0
            progress_entry.save()

            # Check if all weeks are completed
            all_completed = all(
                entry.value == 100
                for entry in ProgressEntry.objects.filter(
                    user=request.user,
                    entry_type='goal',
                    title__startswith='C25K Week'
                )
            )

            if all_completed:
                participation.completed = True
                participation.completion_date = timezone.now()
                participation.save()

                # Award achievement
                Achievement.objects.create(
                    user=request.user,
                    title="5K Runner",
                    description="Completed the Couch to 5K Challenge!",
                    points=500
                )

                messages.success(
                    request,
                    'Congratulations! You\'ve completed the Couch to 5K '
                    'challenge!'
                )
            else:
                messages.success(
                    request,
                    f'Week {week_number} progress updated!'
                )

    return redirect(
        'community:challenge_detail',
        challenge_id=challenge.id
    )


@login_required
def join_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    # Check if user is already participating
    existing_participation = ChallengeParticipation.objects.filter(
        user=request.user,
        challenge=challenge
    ).first()

    if existing_participation:
        messages.info(
            request,
            'You are already participating in this challenge!'
        )
        return redirect(
            'community:challenge_detail',
            challenge_id=challenge.id
        )

    # Create new participation
    ChallengeParticipation.objects.create(
        user=request.user,
        challenge=challenge,
        completed=False
    )

    messages.success(
        request,
        f'Successfully joined {challenge.title}!'
    )
    return redirect(
        'community:challenge_detail',
        challenge_id=challenge.id
    )


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(SocialPost, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime(
                        '%B %d, %Y at %I:%M %p'
                    ),
                    'user': {
                        'username': comment.user.username,
                        'profile_picture': (
                            comment.user.userprofile.profile_picture.url
                            if comment.user.userprofile.profile_picture
                            else None
                        )
                    }
                }
            })
        messages.success(
            request,
            'Comment added successfully!'
        )
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        messages.error(
            request,
            'Error adding comment. Please try again.'
        )

    return redirect('community:post_detail', post_id=post_id)
