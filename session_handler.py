#-*- coding:utf-8 -*-
from django.contrib.sessions.models import Session
from TwGantt.models import GanttLock
from django.db import transaction

def showall():
    s = Session.objects.all()
    for i in s:
        data = i.get_decoded()
        print data

def lockG():
    with transaction.atomic():
        l=GanttLock.objects.select_for_update()
        print type(l)

if __name__ == '__main__':
    lockG()