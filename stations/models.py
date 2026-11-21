from django.db import models

class Station(models.Model):
    STATUS = [('online', 'Online'), ('limited', 'Limited link'), ('offline', 'Offline')]
    name = models.CharField(max_length=60)
    location = models.CharField(max_length=120)
    established = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS, default='online')
    personnel = models.PositiveIntegerField(default=0)
    capacity = models.PositiveIntegerField(default=25)
    summary = models.TextField(blank=True)
    latitude = models.FloatField(default=-70)
    longitude = models.FloatField(default=0)
    class Meta: ordering = ['established']
    def __str__(self): return self.name
    @property
    def latest(self): return self.telemetry.order_by('-recorded_at').first()

class Telemetry(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='telemetry')
    recorded_at = models.DateTimeField()
    temperature = models.FloatField(help_text='°C')
    wind_speed = models.FloatField(help_text='km/h')
    power_kw = models.FloatField()
    fuel_pct = models.FloatField()
    link_mbps = models.FloatField()

class Supply(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='supplies')
    item = models.CharField(max_length=80)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20)
    minimum = models.PositiveIntegerField()
    class Meta: verbose_name_plural = 'supplies'
    @property
    def low(self): return self.quantity <= self.minimum
    @property
    def pct(self): return min(100, int(self.quantity / max(self.minimum * 3, 1) * 100))

class Incident(models.Model):
    SEV = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='incidents')
    title = models.CharField(max_length=140)
    severity = models.CharField(max_length=6, choices=SEV, default='low')
    resolved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['resolved', '-created']

class Command(models.Model):
    ACTIONS = [('heating', 'Adjust base heating'), ('generator', 'Switch generator'), ('comms', 'Reset satellite link'),
               ('lab', 'Lock down laboratory'), ('snapshot', 'Request full data sync')]
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='commands')
    action = models.CharField(max_length=12, choices=ACTIONS)
    note = models.CharField(max_length=160, blank=True)
    issued_by = models.CharField(max_length=60)
    issued_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-issued_at']
    @property
    def state(self):
        from django.utils import timezone
        age = (timezone.now() - self.issued_at).total_seconds()
        if self.station.status == 'offline': return 'Pending: no link'
        return 'Queued' if age < 15 else 'Delivered' if age < 40 else 'Acknowledged'

class Person(models.Model):
    HEALTH = [('fit', 'Fit'), ('observation', 'Under observation'), ('rest', 'Medical rest')]
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='people')
    name = models.CharField(max_length=80)
    role = models.CharField(max_length=60)
    health = models.CharField(max_length=12, choices=HEALTH, default='fit')
    class Meta: ordering = ['station', 'name']
