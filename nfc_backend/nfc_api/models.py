from django.db import models

class Scan(models.Model):
    uid = models.CharField(max_length=100)
    atr = models.CharField(max_length=255, blank=True, null=True)
    raw_data = models.TextField(blank=True, null=True)
    decoded_data = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan {self.uid} at {self.timestamp}"
