"""Real data: Open-Meteo weather (no key) and NOAA SWPC planetary Kp index (no key). Falls back to simulation if offline."""
import json, time, urllib.request
_cache = {}

def _get(url, ttl):
    hit = _cache.get(url)
    if hit and time.time() - hit[0] < ttl: return hit[1]
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'polar-ops-demo'})
        with urllib.request.urlopen(req, timeout=3) as r: data = json.load(r)
        _cache[url] = (time.time(), data)
    except Exception:
        data = hit[1] if hit else None
        _cache[url] = (time.time() - ttl + 60, data)      # retry in a minute
    return data

def weather(s):
    cur = ('temperature_2m,wind_speed_10m,wind_gusts_10m,wind_direction_10m,relative_humidity_2m,surface_pressure,cloud_cover')
    d = _get(f'https://api.open-meteo.com/v1/forecast?latitude={s.latitude}&longitude={s.longitude}&current={cur}', 600)
    c = (d or {}).get('current')
    if not c or c.get('temperature_2m') is None: return None
    return {'temperature': c['temperature_2m'], 'wind': c['wind_speed_10m'], 'gust': c['wind_gusts_10m'], 'dir': c['wind_direction_10m'],
            'humidity': c['relative_humidity_2m'], 'pressure': round(c['surface_pressure']), 'cloud': c['cloud_cover']}

def kp():
    d = _get('https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json', 600)
    try:
        last = d[-1]
        v = last.get('Kp', last.get('kp_index')) if isinstance(last, dict) else last[1]
        return round(float(v), 1)
    except Exception:
        return None

def kp_label(v):
    return '—' if v is None else 'Quiet' if v < 4 else 'Unsettled' if v < 5 else 'Storm: HF/satellite comms at risk' if v < 7 else 'Severe storm'
