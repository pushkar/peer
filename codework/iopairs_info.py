from django.contrib import messages
from codework.models import *

import random

def pair_add(a, i, o):
    return IOPair.objects.get_or_create(assignment=a, input=i, output=o)[1]

def pair_get_all(a):
    return IOPair.objects.filter(assignment=a)

def pair_get_random(a):
    pairs = IOPair.objects.filter(assignment=a)
    return random.sample(pairs, 1)[0]
