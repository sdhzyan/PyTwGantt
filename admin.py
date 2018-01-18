# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Role,Task,Assignment,GanttLog,GanttLock

# Register your models here.

class RoleAdmin(admin.ModelAdmin):
    list_display = ['name',]

class TaskAdmin(admin.ModelAdmin):
    list_display = ['name','start','end','progress','status',]

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['task','resource','role','effort']

class GanttLogAdmin(admin.ModelAdmin):
    list_display = ['user','timest']

class GanttLockAdmin(admin.ModelAdmin):
    list_display = ['user','timest']

admin.site.register(Role,RoleAdmin)
admin.site.register(Task,TaskAdmin)
admin.site.register(Assignment,AssignmentAdmin)
admin.site.register(GanttLock,GanttLockAdmin)
admin.site.register(GanttLog,GanttLogAdmin)