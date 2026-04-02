from django.contrib import admin
from .models import Profile, Activity, NutritionLog, SocialGroup, DailyStats

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'daily_calorie_target', 'created_at')
    search_fields = ('user__username', 'goal')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'duration_minutes', 'distance_km', 'calories_burned', 'start_time')
    list_filter = ('type', 'start_time')

@admin.register(NutritionLog)
class NutritionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'food_name', 'calories', 'protein', 'health_score', 'logged_at')
    list_filter = ('logged_at',)

@admin.register(SocialGroup)
class SocialGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'is_private', 'created_at')
    filter_horizontal = ('members',)

@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'steps', 'sleep_hours')
    list_filter = ('date',)
