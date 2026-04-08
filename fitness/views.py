from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Activity, NutritionLog, DailyStats, SocialGroup
from .services.ai import AIService
import tempfile
import json
import os
from datetime import datetime, timedelta, date

ai_service = AIService()

from django.http import JsonResponse

@login_required
def update_steps(request):
    if request.method == "POST":
        data = json.loads(request.body)
        new_steps = int(data.get("steps", 0))

        stats, _ = DailyStats.objects.get_or_create(
            user=request.user,
            date=date.today()
        )

        if new_steps > stats.steps:
            stats.steps = new_steps
            stats.save()

        return JsonResponse({"status": "ok"})

@login_required
def analyze_meal(request):
    if request.method == "POST" and request.FILES.get("meal_image"):
        image = request.FILES["meal_image"]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            for chunk in image.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        analysis = ai_service.analyze_meal_image(tmp_path)
        os.remove(tmp_path)

        return JsonResponse(analysis)

    return JsonResponse({"error": "Invalid request"})

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('fitness:dashboard')
    return render(request, 'fitness/landing.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user) # Create empty profile
            login(request, user)
            return redirect('fitness:onboarding')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def onboarding(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.age = request.POST.get('age')
        profile.gender = request.POST.get('gender')
        profile.height = request.POST.get('height')
        profile.weight = request.POST.get('weight')
        profile.work_type = request.POST.get('work_type')
        profile.goal = request.POST.get('goal')
        
        # Simple AI-inspired logic for targets
        # BMR estimate (Mifflin-St Jeor)
        if profile.gender == 'M':
            bmr = 10 * float(profile.weight) + 6.25 * float(profile.height) - 5 * int(profile.age) + 5
        else:
            bmr = 10 * float(profile.weight) + 6.25 * float(profile.height) - 5 * int(profile.age) - 161
            
        activity_multipliers = {'S': 1.2, 'A': 1.55, 'VA': 1.9}
        tdee = bmr * activity_multipliers.get(profile.work_type, 1.2)
        
        if profile.goal == 'WL':
            profile.daily_calorie_target = int(tdee - 500)
            profile.protein_target = int(float(profile.weight) * 2.0)
        elif profile.goal == 'MG':
            profile.daily_calorie_target = int(tdee + 300)
            profile.protein_target = int(float(profile.weight) * 2.2)
        else:
            profile.daily_calorie_target = int(tdee)
            profile.protein_target = int(float(profile.weight) * 1.6)
            
        profile.save()
        return redirect('fitness:dashboard')
        
    return render(request, 'fitness/onboarding.html', {'profile': profile})

@login_required
def dashboard(request):

    user = request.user
    today = date.today()

    stats, _ = DailyStats.objects.get_or_create(user=user, date=today)
    profile = getattr(user, 'profile', None)

    # Activities
    recent_activities = Activity.objects.filter(user=user).order_by('-start_time')[:5]

    # Nutrition (TODAY)
    nutrition_today = NutritionLog.objects.filter(
        user=user,
        logged_at__date=today
    ).order_by('-logged_at')

    # Totals
    total_calories = sum(n.calories for n in nutrition_today)
    total_protein = sum(n.protein for n in nutrition_today)
    total_carbs = sum(n.carbs for n in nutrition_today)
    total_fats = sum(n.fats for n in nutrition_today)

    # Progress %
    step_pct = min(100, (stats.steps / 10000) * 100) if stats.steps else 0

    cal_pct = 0
    if profile and profile.daily_calorie_target:
        cal_pct = min(100, (total_calories / profile.daily_calorie_target) * 100)

    sleep_pct = min(100, (stats.sleep_hours / 8) * 100) if stats.sleep_hours else 0

    # AI Insight
    user_data = {
        'goal': profile.get_goal_display() if profile else 'Maintenance',
        'steps': stats.steps,
        'calories': total_calories,
        'protein': total_protein
    }

    ai_insight = ai_service.get_coach_insight(
        user_data,
        list(recent_activities.values('type', 'duration_minutes'))
    )

    context = {
        'stats': stats,
        'profile': profile,
        'recent_activities': recent_activities,

        'nutrition_today': nutrition_today,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fats': total_fats,

        'step_pct': step_pct,
        'cal_pct': cal_pct,
        'sleep_pct': sleep_pct,

        'ai_insight': ai_insight,
        'active_page': 'dashboard',
    }

    return render(request, 'fitness/dashboard.html', context)


@login_required
def gps_tracker(request):
    return render(request, 'fitness/gps_tracker.html', {'active_page': 'activity'})

@login_required
def track_activity(request):
    if request.method == 'POST':
        Activity.objects.create(
            user=request.user,
            type=request.POST.get('type'),
            duration_minutes=request.POST.get('duration_minutes'),
            distance_km=request.POST.get('distance_km', 0),
            calories_burned=int(request.POST.get('duration_minutes')) * 5 # Simple estimate
        )
        return redirect('fitness:dashboard')
    return render(request, 'fitness/activity_log.html')

@login_required
def log_nutrition(request):
    if request.method == 'POST':
        # Manual log for now
        NutritionLog.objects.create(
            user=request.user,
            food_name=request.POST.get('food_name'),
            calories=request.POST.get('calories'),
            protein=request.POST.get('protein', 0),
            carbs=request.POST.get('carbs', 0),
            fats=request.POST.get('fats', 0),
        )
        return redirect('fitness:dashboard')
    return render(request, 'fitness/nutrition_log.html')

@login_required
def coach_chat(request):

    # 🖼️ IMAGE UPLOAD FIRST
    if request.method == 'POST' and request.FILES.get('meal_image'):
        image = request.FILES['meal_image']

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in image.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        analysis = ai_service.analyze_meal_image(tmp_path)
        os.remove(tmp_path)
        
        log = NutritionLog.objects.create(
            user=request.user,
            food_name=analysis.get('food_name', 'AI Detected Meal'),
            calories=analysis.get('calories', 0),
            protein=analysis.get('protein', 0),
            carbs=analysis.get('carbs', 0),
            fats=analysis.get('fats', 0),
            health_score=analysis.get('health_score', 50),
            image=image
        )

        return redirect('fitness:dashboard')

    # 💬 CHAT
    if request.method == 'POST':
        user_message = request.POST.get('message')
        profile = getattr(request.user, 'profile', None)
        
        context_data = {
            'goal': profile.get_goal_display() if profile else 'Maintenance',
            'weight': profile.weight if profile else 70,
        }
        
        ai_response = ai_service.get_coach_insight(context_data, user_message)

        return render(request, 'fitness/includes/chat_snippet.html', {
            'user_message': user_message,
            'ai_response': ai_response
        })

    return render(request, 'fitness/coach_chat.html', {'active_page': 'coach'})

# views.py

@login_required
def voice_log(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio = request.FILES['audio']

        # Save as WEBM (NOT WAV ❗)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            for chunk in audio.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        print("📁 Saved audio:", tmp_path)

        # Transcribe
        text = ai_service.transcribe_voice_meal(tmp_path)

        # Cleanup
        os.remove(tmp_path)

        print("🧠 Final text:", text)

        # Save
        NutritionLog.objects.create(
            user=request.user,
            food_name=f"Voice Log: {text[:50]}...",
            calories=300,
            ai_metadata={'transcription': text}
        )

        return redirect('fitness:dashboard')

    return render(request, 'fitness/voice_log.html')

@login_required
def community_feed(request):
    # Show activities from all users for the "Social Loop"
    activities = Activity.objects.all().order_by('-start_time')[:20]
    groups = SocialGroup.objects.filter(members=request.user)
    
    context = {
        'activities': activities,
        'groups': groups,
        'active_page': 'community',
    }
    return render(request, 'fitness/community.html', context)

@login_required
def join_group(request, group_id):
    group = SocialGroup.objects.get(id=group_id)
    group.members.add(request.user)
    return redirect('fitness:community')

@login_required
def save_ai_meal(request):
    import json

    if request.method == "POST":
        data = json.loads(request.body)

        NutritionLog.objects.create(
            user=request.user,
            food_name=data.get("food_name"),
            calories=data.get("calories"),
            protein=data.get("protein"),
            carbs=data.get("carbs"),
            fats=data.get("fats"),
            health_score=data.get("health_score", 50),
        )

        return JsonResponse({"status": "saved"})


@login_required
def log_sleep(request):
    if request.method == "POST":
        sleep_start = request.POST.get("sleep_start") 
        start_period = request.POST.get("start_period")

        sleep_end = request.POST.get("sleep_end")
        end_period = request.POST.get("end_period")

        start_dt = datetime.strptime(f"{sleep_start} {start_period}", "%I:%M %p")
        end_dt = datetime.strptime(f"{sleep_end} {end_period}", "%I:%M %p")

        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        sleep_hours = (end_dt - start_dt).seconds / 3600

        if sleep_hours < 6:
            quality = "Low"
        elif sleep_hours <= 8:
            quality = "Good"
        else:
            quality = "High"

        stats, _ = DailyStats.objects.get_or_create(
            user=request.user,
            date=date.today()
        )

        stats.sleep_hours = round(sleep_hours, 1)
        stats.sleep_start = start_dt.time()
        stats.sleep_end = end_dt.time()
        stats.sleep_quality = quality
        stats.save()

        return redirect("fitness:dashboard")

    return render(request, "fitness/sleep_log.html")