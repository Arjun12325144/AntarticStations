import csv, math
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from . import simulator, external
from .models import *

def _counts():
    return Incident.objects.filter(resolved=False).count(), sum(1 for x in Supply.objects.all() if x.low)

@login_required
def dashboard(r):
    st = list(Station.objects.all())
    for s in st:
        simulator.advance(s)
        rad, a = (90 + s.latitude) / 40 * 110, math.radians(s.longitude)
        s.px, s.py, s.live_src = round(120 + rad * math.sin(a), 1), round(120 - rad * math.cos(a), 1), bool(external.weather(s))
    kp = external.kp(); oc, lc = _counts()
    return render(r, 'dashboard.html', {'stations': st, 'people': sum(s.personnel for s in st), 'open_count': oc, 'low_count': lc,
                                        'kp': kp, 'kp_label': external.kp_label(kp), 'events': Command.objects.select_related('station')[:5]})

@login_required
def station(r, pk):
    s = get_object_or_404(Station, pk=pk); simulator.advance(s)
    t = list(s.telemetry.order_by('-recorded_at')[:40])[::-1]
    ext = external.weather(s)
    series = {'temp': [x.temperature for x in t], 'power': [x.power_kw for x in t], 'wind': [x.wind_speed for x in t]}
    return render(r, 'station.html', {'s': s, 'series': series, 'ext': ext or {}, 'live_src': bool(ext), 'commands': s.commands.all()[:6],
                                      'actions': Command.ACTIONS, 'people': s.people.all()[:8]})

@login_required
@require_POST
def send_command(r, pk):
    s = get_object_or_404(Station, pk=pk); a = r.POST.get('action')
    if a in dict(Command.ACTIONS):
        Command.objects.create(station=s, action=a, note=r.POST.get('note', '')[:160], issued_by=r.user.get_username())
        messages.success(r, f'{dict(Command.ACTIONS)[a]} queued for {s.name}.')
    return redirect('station', pk=pk)

@login_required
def supplies(r):
    return render(r, 'supplies.html', {'stations': Station.objects.prefetch_related('supplies')})

@login_required
def people(r):
    return render(r, 'people.html', {'items': Person.objects.select_related('station'), 'stations': Station.objects.filter(personnel__gt=0)})

@login_required
def incidents(r):
    if r.method == 'POST':
        if r.POST.get('resolve'):
            Incident.objects.filter(pk=r.POST['resolve']).update(resolved=True); messages.success(r, 'Incident resolved.')
        elif r.POST.get('title'):
            Incident.objects.create(station_id=r.POST['station'], title=r.POST['title'][:140], severity=r.POST.get('severity', 'low')); messages.success(r, 'Incident logged.')
        return redirect('incidents')
    return render(r, 'incidents.html', {'items': Incident.objects.select_related('station'), 'stations': Station.objects.all()})

@login_required
def export(r, pk):
    s = get_object_or_404(Station, pk=pk)
    resp = HttpResponse(content_type='text/csv'); resp['Content-Disposition'] = f'attachment; filename="{s.name.replace(" ", "_")}_telemetry.csv"'
    w = csv.writer(resp); w.writerow(['time', 'temp_c', 'wind_kmh', 'power_kw', 'fuel_pct', 'link_mbps'])
    for t in s.telemetry.order_by('recorded_at'): w.writerow([t.recorded_at.isoformat(), t.temperature, t.wind_speed, t.power_kw, t.fuel_pct, t.link_mbps])
    return resp

@login_required
def live(r):
    out = []
    for s in Station.objects.all():
        t = simulator.advance(s); s.refresh_from_db(); e = external.weather(s) or {}
        out.append({'id': s.pk, 'status': s.status, 'status_label': s.get_status_display(), 'temperature': t.temperature, 'wind_speed': t.wind_speed,
                    'power_kw': t.power_kw, 'link_mbps': t.link_mbps, 'fuel_pct': round(t.fuel_pct), 'humidity': e.get('humidity'),
                    'pressure': e.get('pressure'), 'gust': e.get('gust'), 'wind_dir': e.get('dir'), 'cloud': e.get('cloud')})
    oc, lc = _counts(); kp = external.kp()
    return JsonResponse({'stations': out, 'time': timezone.localtime().strftime('%H:%M:%S'), 'open_count': oc, 'low_count': lc,
                         'kp': kp if kp is not None else '—'})
