import md5
from datetime import datetime, timedelta
from .models import LoginBruteForceSecurity
from django.conf import settings

try: 
    BRUTE_FORCE_THRESHOLD = settings.BRUTE_FORCE_THRESHOLD
except:
    BRUTE_FORCE_THRESHOLD = 5
    
try:
    BRUTE_FORCE_RESET_THRESHOLD = settings.BRUTE_FORCE_RESET_THRESHOLD 
except:
    BRUTE_FORCE_RESET_THRESHOLD = 300 #in seconds
    
try:
    BRUTE_FORCE_PURGE_MULTIPLIER = settings.BRUTE_FORCE_PURGE_MULTIPLIER
except:
    BRUTE_FORCE_PURGE_MULTIPLIER = 2   

def brute_force_add(ip, entry=None):
    """
       Adds a new entry to the brute force table or updates an old one
       IP-Addresses are saved as MD5 hashes to avoid privacy problems 
       in states like germany
    """
    ip_hash = md5.new(ip).hexdigest()
    if entry == None:
        new, entry = LoginBruteForceSecurity.objects.get_or_create(
            ip_hash=ip_hash,
            )
        if not new:
            entry.login_count=1
            entry.save()
    else:
        entry.login_count = entry.login_count + 1
        entry.save()
    return entry
    

def brute_force_check(ip):
    """
        Returns None if there is no entry for the given ip, so no attack yet
        Returns False if the the login_count is exceeds the threshold and the 
            time from the last login error is inside the reset threshold
        Returns the entry if there is one but the threshold is not exceeded.
    """
    ip_hash = md5.new(ip).hexdigest()
    try:
        entry = LoginBruteForceSecurity.objects.get(ip_hash=ip_hash)
        if entry.last_try + timedelta(seconds=BRUTE_FORCE_RESET_THRESHOLD) > datetime.now():
            if entry.login_count >= BRUTE_FORCE_THRESHOLD:
                return False
            else:
                return entry
        else:
            #if time is up but there is still a entry in the databse, reset it and return it
            entry.login_count = 0
            entry.save()
            return entry
    except LoginBruteForceSecurity.DoesNotExist:
        return None
        
def brute_force_purge(threshold=BRUTE_FORCE_RESET_THRESHOLD, multiplier=BRUTE_FORCE_PURGE_MULTIPLIER):
    """
        Deletes all old entries that are older than the given threshold times
        the given multiplier.
        Try to keep your table small to keep the process as fast as possible
    """
    obj = LoginBruteForceSecurity.objects.filter(last_try__lte=datetime.now()-timedelta(seconds=threshold*multiplier)).delete()
    
