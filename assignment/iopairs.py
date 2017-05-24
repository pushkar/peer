import random
import logging
from django.contrib import messages
from assignment.models import IOPair

log = logging.getLogger(__name__)

def add(a, i, o):
    ret = IOPair.objects.get_or_create(assignment=a, input=i, output=o)
    if ret[1] is True:
        log.info("IOPair added successfully")
    else:
        log.error("Failed to add IOPair")
    return ret[1]

def get_none():
    return IOPair.objects.none()

def get(a):
    return IOPair.objects.filter(assignment=a)

def get_by_id(id):
    return IOPair.objects.filter(pk=id)

def get_random(a, count=1):
    pairs = IOPair.objects.filter(assignment=a)
    return random.sample(list(pairs), count)
