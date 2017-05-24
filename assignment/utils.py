from django.http import HttpResponseRedirect
from django.utils.translation import ngettext
from datetime import timedelta

def force_logout(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('student:index'))

def localize_timedelta(delta):
    ret = []
    num_years = int(delta.days / 365)
    if num_years > 0:
        delta -= timedelta(days=num_years * 365)
        ret.append(ngettext('%d year', '%d years', num_years) % num_years)

    if delta.days > 0:
        ret.append(ngettext('%d day', '%d days', delta.days) % delta.days)

    num_hours = int(delta.seconds / 3600)
    if num_hours > 0:
        delta -= timedelta(hours=num_hours)
        ret.append(ngettext('%d hour', '%d hours', num_hours) % num_hours)

    num_minutes = int(delta.seconds / 60)
    if num_minutes > 0:
        ret.append(ngettext('%d minute', '%d minutes', num_minutes) % num_minutes)

    return ' '.join(ret)
    