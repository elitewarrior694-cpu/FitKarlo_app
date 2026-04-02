from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    GOAL_CHOICES = [
        ('WL', 'Weight Loss'),
        ('MG', 'Muscle Gain'),
        ('MT', 'Maintenance'),
    ]
    WORK_TYPE_CHOICES = [
        ('S', 'Sedentary'),
        ('A', 'Active'),
        ('VA', 'Very Active'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    height = models.FloatField(help_text="Height in cm", null=True, blank=True)
    weight = models.FloatField(help_text="Weight in kg", null=True, blank=True)
    work_type = models.CharField(max_length=2, choices=WORK_TYPE_CHOICES, default='S')
    goal = models.CharField(max_length=2, choices=GOAL_CHOICES, default='MT')
    daily_calorie_target = models.PositiveIntegerField(default=2000)
    protein_target = models.PositiveIntegerField(default=150, help_text="Target protein in grams")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('RUN', 'Running'),
        ('WALK', 'Walking'),
        ('CYCL', 'Cycling'),
        ('WORK', 'Workout'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    type = models.CharField(max_length=4, choices=ACTIVITY_TYPES)
    start_time = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField()
    distance_km = models.FloatField(default=0.0)
    calories_burned = models.PositiveIntegerField()
    heart_rate_avg = models.PositiveIntegerField(null=True, blank=True)
    gps_data = models.JSONField(null=True, blank=True, help_text="Stored route coordinates")

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()} ({self.start_time.date()})"

class NutritionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_logs')
    food_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='meals/', null=True, blank=True)
    calories = models.PositiveIntegerField()
    protein = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)
    fats = models.FloatField(default=0.0)
    health_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=50)
    ai_metadata = models.JSONField(null=True, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.food_name}"

class SocialGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administered_groups')
    members = models.ManyToManyField(User, related_name='fitness_groups')
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DailyStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField(auto_now_add=True)
    steps = models.PositiveIntegerField(default=0)
    sleep_hours = models.FloatField(default=0.0)
    water_intake_ml = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} Stats - {self.date}"
