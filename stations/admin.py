from django.contrib import admin
from .models import *
for m in (Person, Station, Telemetry, Supply, Incident, Command): admin.site.register(m)
