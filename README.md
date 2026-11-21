# Polar Ops – Indian Antarctic station management (Django + SQLite)
    pip install django
    python manage.py migrate && python manage.py seed
    python manage.py runserver
Login: admin / admin123 (change it). Admin panel at /admin/.

## Deploy to Vercel
See chat instructions: push to GitHub, import the repo in Vercel, set SECRET_KEY, deploy.
Note: on Vercel the SQLite database lives in /tmp and resets on cold starts (demo use only).
