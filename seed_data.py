import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitkarlo.settings')
django.setup()

from django.contrib.auth.models import User
from fitness.models import Profile, Activity, SocialGroup, NutritionLog

def seed_data():
    # Create or get users
    u1, _ = User.objects.get_or_create(username='IronMan', email='iron@fitkarlo.com')
    u2, _ = User.objects.get_or_create(username='WonderWoman', email='wonder@fitkarlo.com')
    
    # Ensure they have profiles
    Profile.objects.get_or_create(user=u1, defaults={'goal': 'MG', 'weight': 85, 'height': 185, 'age': 35})
    Profile.objects.get_or_create(user=u2, defaults={'goal': 'WL', 'weight': 65, 'height': 175, 'age': 30})

    # Create Groups
    g1, _ = SocialGroup.objects.get_or_create(
        name='Muscle Gain Elite', 
        defaults={'admin': u1, 'description': 'The ultimate group for those seeking peak hypertrophy.'}
    )
    g2, _ = SocialGroup.objects.get_or_create(
        name='Early Morning Walkers', 
        defaults={'admin': u2, 'description': 'Kickstart your metabolism with 5am walks.'}
    )
    
    g1.members.add(u1, u2)
    g2.members.add(u2)

    # Create Activities
    Activity.objects.get_or_create(
        user=u1, type='RUN',
        defaults={
            'duration_minutes': 45, 'distance_km': 8.5, 'calories_burned': 520,
            'start_time': timezone.now() - timedelta(hours=2)
        }
    )
    Activity.objects.get_or_create(
        user=u2, type='WALK',
        defaults={
            'duration_minutes': 30, 'distance_km': 3.2, 'calories_burned': 180,
            'start_time': timezone.now() - timedelta(hours=5)
        }
    )

    print("Seed data created successfully!")

if __name__ == '__main__':
    seed_data()
