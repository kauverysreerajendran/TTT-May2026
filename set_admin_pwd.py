import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchcase_tracker.settings')
django.setup()

from django.contrib.auth.models import User
u = User.objects.get(username='admin')
u.set_password('admin')
u.save()
print('Password set to: admin')
