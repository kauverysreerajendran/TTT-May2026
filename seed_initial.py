"""
Initial seed script: creates admin user and TrayType master records.
Run as: env\Scripts\python.exe seed_initial.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchcase_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from modelmasterapp.models import TrayType

# Create admin superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@ttt.local', 'admin@123')
    print('✅ Admin user created (username=admin, password=admin@123)')
else:
    print('ℹ️  Admin user already exists')

# Create TrayType records
normal, created = TrayType.objects.get_or_create(
    tray_type='Normal', defaults={'tray_capacity': 16}
)
print(f'{"✅ Created" if created else "ℹ️  Exists"} Normal tray type (capacity={normal.tray_capacity})')

jumbo, created = TrayType.objects.get_or_create(
    tray_type='Jumbo', defaults={'tray_capacity': 12}
)
print(f'{"✅ Created" if created else "ℹ️  Exists"} Jumbo tray type (capacity={jumbo.tray_capacity})')

print('\nDone.')
