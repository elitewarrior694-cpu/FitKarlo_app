from django.urls import path
from . import views

app_name = 'fitness'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('track-activity/', views.track_activity, name='track_activity'),
    path('gps-tracker/', views.gps_tracker, name='gps_tracker'),
    path('coach-chat/', views.coach_chat, name='coach_chat'),
    path('log-nutrition/', views.log_nutrition, name='log_nutrition'),
    path('analyze-meal/', views.analyze_meal, name='analyze_meal'),
    path('save-ai-meal/', views.save_ai_meal, name='save_ai_meal'),
    path('voice-log/', views.voice_log, name='voice_log'),
    path('community/', views.community_feed, name='community'),
    path('groups/join/<int:group_id>/', views.join_group, name='join_group'),
    path("update_steps/", views.update_steps, name="update_steps"),
    path('sleep/', views.log_sleep, name='log_sleep'),
]
