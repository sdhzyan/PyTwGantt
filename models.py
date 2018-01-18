# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from .dthandler import utc_to_cn_str

# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=50,null=False,verbose_name=u'角色名称')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'角色'
        verbose_name_plural = u'角色集'

# class Resource(models.Model):
#     name = models.CharField(max_length=50,null=False,verbose_name=u'资源名称')

class Task(models.Model):
    #task_id = models.IntegerField(unique=True,null=False,primary_key=True,verbose_name=u'序号')
    task_order = models.IntegerField(null=False, verbose_name=u'顺序序号')
    name = models.CharField(max_length=100,null=False,verbose_name=u'名称')
    progress = models.IntegerField(verbose_name=u'进度(%)')
    progressByWorklog = models.BooleanField(null=False,default=False,verbose_name=u'是否按工作日志设置进度')
    relevance = models.IntegerField(verbose_name=u'relevance')
    type = models.CharField(null=True,max_length=30,verbose_name=u'type')
    typeId = models.CharField(null=True,max_length=10,verbose_name=u'typeId')
    description = models.TextField(max_length=300,verbose_name=u'描述')
    code = models.CharField(max_length=10,verbose_name=u'代号')
    level = models.IntegerField(null=False,verbose_name=u'层级')
    status = models.CharField(max_length=50,verbose_name=u'状态')
    depends = models.CharField(max_length=50,verbose_name=u'依赖')
    # canWrite = models.BooleanField(null=False,default=True,verbose_name=u'是否可以修改')
    start = models.DateTimeField(null=False,verbose_name=u'开始时间戳')
    duration = models.IntegerField(null=False,verbose_name=u'持续时间(天)')
    end = models.DateTimeField(null=False,verbose_name=u'结束时间戳')
    startIsMilestone = models.BooleanField(null=False,default=False,verbose_name=u'开始时间是否里程碑')
    endIsMilestone = models.BooleanField(null=False,default=False,verbose_name=u'结束时间是否里程碑')
    collapsed = models.BooleanField(null=False,default=False,verbose_name=u'是否折叠')
    hasChild = models.BooleanField(null=False,default=False,verbose_name=u'是否有子任务')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'任务'
        verbose_name_plural = u'任务集'

class Assignment(models.Model):
    task = models.ForeignKey(Task,verbose_name=u'任务')
    resource = models.ForeignKey(User,verbose_name=u'资源')
    role = models.ForeignKey(Role,verbose_name=u'角色')
    effort = models.DecimalField(null=False,max_digits=22,decimal_places=2,verbose_name=u'工作量')

    def __unicode__(self):
        return self.task.name+r'('+str(self.id)+r')'

    class Meta:
        verbose_name = u'任务指派'
        verbose_name_plural = u'任务指派集'

class GanttLog(models.Model):
    opruid = models.CharField(max_length=255,verbose_name=u'操作UID')
    user = models.ForeignKey(User,verbose_name=u'修改人')
    to_model = models.CharField(max_length=100,verbose_name=u'修改对象')
    to_model_id = models.IntegerField(verbose_name=u'修改对象ID')
    timest = models.DateTimeField(auto_now=True,verbose_name=u'修改时间')

    def __unicode__(self):
        return "第%d次修改by%s" %(self.id,(self.user.first_name+self.user.last_name) if (self.user.first_name+self.user.last_name) else self.user)

    class Meta:
        verbose_name = u'修改日志'
        verbose_name_plural = u'修改历史'

class GanttLock(models.Model):
    user = models.CharField(max_length=50,blank=True,null=True,verbose_name=u'资源锁持有者')
    timest = models.DateTimeField(auto_now=True,verbose_name=u'资源锁定时间')

    def __unicode__(self):
        return "%s于%s锁定编辑" %(self.user,utc_to_cn_str(self.timest))

    class Meta:
        verbose_name = u'锁日志'
        verbose_name_plural = u'锁日志'