from django.db import models

class LoginBruteForceSecurity(models.Model):
    ip_hash = models.CharField(max_length=32, null=True, blank=True)
    login_count = models.IntegerField(null=True, blank=True)
    last_try = models.DateTimeField(auto_now=True)
    
