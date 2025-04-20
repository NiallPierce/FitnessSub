from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_home, name='home'),
    path('challenges/', views.challenges, name='challenges'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('social-feed/', views.social_feed, name='social_feed'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('group-workouts/', views.group_workouts, name='group_workouts'),
    path('group-workouts/create/', views.create_workout, name='create_workout'),
    path('group-workouts/<int:workout_id>/', views.workout_detail, name='workout_detail'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
] 