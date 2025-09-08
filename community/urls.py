from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_home, name='community_home'),
    path('challenges/', views.challenges, name='challenges'),
    path('challenges/c25k/', views.c25k_challenge, name='c25k_challenge'),
    path(
        'challenges/c25k/start/',
        views.start_c25k_challenge,
        name='start_c25k_challenge'
    ),
    path(
        'challenges/c25k/update/',
        views.update_c25k_progress,
        name='update_c25k_progress'
    ),
    path('social/', views.social_feed, name='social_feed'),
    path('social/create/', views.create_post, name='create_post'),
    path(
        'social/<int:post_id>/edit/',
        views.edit_post,
        name='edit_post'
    ),
    path(
        'social/<int:post_id>/delete/',
        views.delete_post,
        name='delete_post'
    ),
    path(
        'social/<int:post_id>/',
        views.post_detail,
        name='post_detail'
    ),
    path('workouts/', views.group_workouts, name='group_workouts'),
    path('workouts/create/', views.create_workout, name='create_workout'),
    path(
        'workouts/<int:workout_id>/',
        views.workout_detail,
        name='workout_detail'
    ),
    path(
        'workouts/<int:workout_id>/join/',
        views.join_workout,
        name='join_workout'
    ),
    path(
        'workouts/<int:workout_id>/leave/',
        views.leave_workout,
        name='leave_workout'
    ),
    path(
        'workouts/<int:workout_id>/edit/',
        views.edit_workout,
        name='edit_workout'
    ),
    path(
        'workouts/<int:workout_id>/delete/',
        views.delete_workout,
        name='delete_workout'
    ),
    path(
        'profile/<str:username>/',
        views.user_profile,
        name='user_profile'
    ),
]
