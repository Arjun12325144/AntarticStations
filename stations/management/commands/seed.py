import random
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from stations import simulator
from stations.models import Person, Station, Telemetry, Supply, Incident, Command as Cmd

class Command(BaseCommand):
    def handle(self, *a, **k):
        if Station.objects.exists(): return
        if not User.objects.filter(username='admin').exists(): User.objects.create_superuser('admin', '', 'admin123')
        data = [('Dakshin Gangotri', 'Princess Astrid Coast, Dronning Maud Land', -70.08, 12.0, 1983, 'offline', 0, 'India’s first station, now a supply base buried by the ice shelf.'),
                ('Maitri', 'Schirmacher Oasis, East Antarctica', -70.77, 11.73, 1989, 'online', 24, 'Year-round research station on a granite outcrop with freshwater lakes.'),
                ('Bharati', 'Larsemann Hills, Prydz Bay', -69.41, 76.19, 2012, 'limited', 38, 'Ship-shaped, container-built station for geology and oceanography.')]
        now = timezone.now()
        for n, loc, la, lo, y, stt, p, sm in data:
            s = Station.objects.create(name=n, location=loc, established=y, latitude=la, longitude=lo, status=stt, personnel=p, summary=sm, capacity=47 if n == 'Bharati' else 25)
            simulator.backfill(s, 40)
            F = ['Arjun','Priya','Rahul','Ananya','Vikram','Meera','Sandeep','Kavita','Rohit','Neha','Suresh','Divya','Amit','Pooja','Karan','Sneha','Manoj','Lakshmi','Imran','Harpreet','Deepak','Anjali','Tenzin','Faisal']
            L = ['Sharma','Nair','Reddy','Iyer','Singh','Patel','Das','Menon','Gupta','Kulkarni','Bose','Rao','Khan','Pillai','Joshi','Verma']
            R = ['Glaciologist','Meteorologist','Geologist','Marine biologist','Medical officer','Electrical engineer','Communications officer','Chef','Diesel mechanic','Atmospheric scientist']
            for i in range(p):
                Person.objects.create(station=s, name=f'{random.choice(F)} {random.choice(L)}', role='Station leader' if i == 0 else random.choice(R),
                                      health=random.choices(['fit','observation','rest'], [90, 7, 3])[0])
            for item, q, u, m in [('Diesel (arctic grade)', random.randint(8, 60), 'kL', 15), ('Fresh produce', random.randint(20, 400), 'kg', 90), ('Medical kits', random.randint(4, 30), 'kits', 8), ('Lab reagents', random.randint(10, 80), 'cases', 20)]:
                Supply.objects.create(station=s, item=item, quantity=q, unit=u, minimum=m)
        Incident.objects.create(station_id=3, title='Satellite uplink dropping during katabatic winds', severity='medium')
        Incident.objects.create(station_id=2, title='Generator 2 vibration above threshold', severity='high')
        Cmd.objects.create(station_id=2, action='snapshot', issued_by='admin', note='Weekly sync')
