"""Realistic telemetry simulator: each call to advance() adds readings for the time that has passed."""
import math, random
from datetime import timedelta
from django.utils import timezone
from . import external
from .models import Telemetry, Incident

TICK = 5            # seconds between readings
KEEP = 300          # readings kept per station
BASE = {'Maitri': -12, 'Bharati': -14, 'Dakshin Gangotri': -18}   # mean outside temp (°C)

def _make(s, last, ts, ext=None):
    active = s.personnel > 0
    hour = ts.hour + ts.minute / 60
    target = BASE.get(s.name, -15) + 3 * math.sin((hour - 9) / 24 * 2 * math.pi)   # warmest mid-afternoon
    if ext: target = ext['temperature']      # anchor on the real measurement when available
    wm = ext['wind'] if ext else 28
    temp = target if not last else last.temperature + 0.15 * (target - last.temperature) + random.gauss(0, 0.12)
    wind = wm if not last else last.wind_speed + 0.15 * (wm - last.wind_speed) + random.gauss(0, 2.2)
    if random.random() < 0.02: wind += random.uniform(10, 25)          # katabatic gust
    wind = max(0.0, wind)
    power = 4 + random.gauss(0, .2) if not active else 32 + (-temp) * 3.4 + wind * .25 + random.gauss(0, 2.5)
    fuel = random.uniform(60, 90) if not last else last.fuel_pct - 0.012
    if fuel < 30: fuel = random.uniform(85, 92)                          # resupply delivered
    link = 0.1 if not active else max(0.5, 14 - wind * .16 + random.gauss(0, .8))
    return Telemetry(station=s, recorded_at=ts, temperature=round(temp, 1), wind_speed=round(wind, 1),
                     power_kw=round(max(power, 0), 1), fuel_pct=round(fuel, 2), link_mbps=round(link, 1))

def backfill(s, n=40):
    now, last, ext = timezone.now(), None, external.weather(s)
    for i in range(n, 0, -1):
        last = _make(s, last, now - timedelta(seconds=i * TICK), ext); last.save()
    return last

def advance(s):
    last = s.latest
    if not last: return backfill(s)
    now, ext = timezone.now(), external.weather(s)
    steps = int((now - last.recorded_at).total_seconds() // TICK)
    if steps <= 0: return last
    ts = max(last.recorded_at, now - timedelta(seconds=40 * TICK))
    for _ in range(min(steps, 40)):
        ts += timedelta(seconds=TICK); last = _make(s, last, ts, ext); last.save()
    if s.personnel > 0:
        new = 'limited' if last.link_mbps < 4 or last.wind_speed > 60 else 'online'
        if new != s.status: s.status = new; s.save(update_fields=['status'])
        if last.wind_speed > 65 and not Incident.objects.filter(station=s, resolved=False, title__startswith='High wind').exists():
            Incident.objects.create(station=s, severity='medium', title=f'High wind advisory: gusts {last.wind_speed:.0f} km/h')
    s.telemetry.filter(pk__in=list(s.telemetry.order_by('-recorded_at').values_list('pk', flat=True)[KEEP:])).delete()
    return last
