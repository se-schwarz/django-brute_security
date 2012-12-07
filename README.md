django-brute_security
=====================

Provides simple IP based brute force security for django user login

*Basic Functinality*

This module provides basic functions to check if an IP trys to bruteforce
on or many accounts at your django page.
It also provides posibilities to lock an IP.

*Installation*

The installation is pretty easy.
Put the module into your settings installed_apps.
Resync your database.
Set the following variables in your
projects settings.py (if you dont want to use the default values)

The following variable configures the available login attempts a user
can make before his IP is blocked. If nothing is set in your
settings.py the default of 5 attempts will be used.

<pre>
    BRUTE_FORCE_THRESHOLD = 5
</pre>

The following variable configures the time until a blocked IP is set free, 
and how long the last login can be in the past and still accumulates with
new login errors. Default is 300 seconds (5 minutes)

<pre>
    BRUTE_FORCE_RESET_THRESHOLD = 300 #in seconds
</pre>

Set the BRUTE_FORCE_PURGE_MULTIPLIER variable to set a multiplier which is
used in the purge method that cleans the database of old entries. If you
call brute_force_purge with default values, entries that are older
than the default BRUTE_FORCE_RESET_THRESHOLD times the default BRUTE_FORCE_PURGE_MULTIPLIER
will be deleted. Default is 2

<pre>
    BRUTE_FORCE_PURGE_MULTIPLIER = 2   
</pre>

*Usage*

You should check for brute force attacks prior the validation of the login form.

Use brute_force_check(request.META['REMOTE_ADDR']) to check if the given IP
has a entry in the security database. 

It will return *False* if the IP is blocked at the current time.

It will return an Object if the IP has an entry but is not blocked currently

It will return None if there is no entry for it yet


Use brute_force_add(request.META['REMOTE_ADDR'], [brute_force_object]) to
add or update a entry in the brute_force table. (Use the entry from brute_force_check
as entry attribute to save one database hit).

Use brute_force_purge() to purge old entries and keep the database table clean.

Example:

<pre>
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from brute_security.utils import brute_force_check, brute_force_add

def my_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        bfc_entry = brute_force_check(request.META['REMOTE_ADDR'])
        if bfc_entry == False:
           messages.add_message(request, messages.ERROR, _('Too many login attempts, please try again later.')) 
        else:
            if form.is_valid():
                response = login(request, form.get_user())
                return response
            else:
                brute_force_add(request.META['REMOTE_ADDR'], bfc_entry)        
    else:
        form = AuthenticationForm()
    return render_to_response('my_login_template.html', {
        'form': form,
        }, context_instance=RequestContext(request))
</pre>