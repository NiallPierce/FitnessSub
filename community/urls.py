from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_home, name='community_home'),
    path('challenges/', views.challenges, name='challenges'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:challenge_id>/join/', views.join_challenge, name='join_challenge'),
    path('challenges/c25k/create/', views.create_c25k_challenge, name='create_c25k'),
    path('challenges/c25k/<int:challenge_id>/update/', views.update_c25k_progress, name='update_c25k_progress'),
    path('social/', views.social_feed, name='social_feed'),
    path('social/create/', views.create_post, name='create_post'),
    path('social/<int:post_id>/', views.post_detail, name='post_detail'),
    path('workouts/', views.group_workouts, name='group_workouts'),
    path('workouts/<int:workout_id>/', views.workout_detail, name='workout_detail'),
    path('workouts/create/', views.create_workout, name='create_workout'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
] 