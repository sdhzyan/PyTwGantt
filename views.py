# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from .models import Role,Task,Assignment,GanttLog,GanttLock
from .dthandler import int_to_dt,dt_to_int
from .forms import LoginForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.db import transaction
from django.contrib.sessions.models import Session
from django.urls import reverse
from decimal import Decimal
import json,uuid

# Create your views here.
def user_login(request):
    '''登陆页面'''
    # 会话有效时长1小时
    request.session.set_expiry(60*60)
    # 已登录则直接跳转
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            userpwd = form.cleaned_data['userpwd']
            #清除当前用户其他会话
            clean_user_session(username)
            user = auth.authenticate(username=username,password=userpwd)
            auth.login(request,user)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = LoginForm()
    return render(request,'login.html',{'form':form})

def user_logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required(login_url='/TwGantt/login/')
def return_home(request):
    '''TwGantt首页'''
    try:
        canWrite = 'true' if get_write_permission(request.user.username)['canWrite'] else 'false'
        lockmsg = get_write_permission(request.user.username)['lockmsg']
    except Exception,e:
        print repr(e)
        canWrite = 'false'
        lockmsg = ''

    return render(request,'gantt.html',{'username':request.user.username,'lockmsg':lockmsg,'canWrite':canWrite})

def save_prj(request):
    '''AJAX保存项目数据'''
    if request.is_ajax():
        ori_project = json.loads(request.POST.get('prj'))
        resp = {'ok':True,'project':ori_project,'errorMessages':u'','message':u''}
        resp['project']['canDelete'] = True
        # 检查登录状态,若已在他处登录，则提示会话超时
        if request.user.is_authenticated():
            try:
                resp['project'] = par_prj_json(request.user,json.loads(request.POST.get('prj')))
            except Exception,e:
                print repr(e)
                resp['ok'] = False
                resp['message'] = u'保存出错，请重试'
        else:
            resp['ok'] = False
            resp['message'] = u'会话超时,请重新登录'

        return JsonResponse(resp)
    else:
        return HttpResponse(u'无效请求')

def load_prj(request):
    '''AJAX加载项目数据'''
    if request.is_ajax():
        prj_json = {'ok':True}
        try:
            prj_editable = get_write_permission(request.user.username)['canWrite']
            prj_json['project'] = gen_prj_json(prj_editable=prj_editable)
        except Exception,e:
            print repr(e)
            prj_json['ok'] = False
            prj_json['message'] = u'加载数据出错，请尝试刷新'
        return JsonResponse(prj_json)
    else:
        return HttpResponse(u'无效请求')

@transaction.atomic
def par_prj_json(user,prj_json_data):
    '''解析AJAX提交的项目json数据并更新到数据库中'''

    project = prj_json_data
    tasks = project['tasks']
    # task_index顺序决定task展示顺序
    task_index = 0
    opruid = str(uuid.uuid1())

    # print tasks

    for task in tasks:
        #并发及修改方式未实现
        task_index += 1
        assigs = task['assigs']
        #print task
        tskid = task['id']
        if str(tskid).startswith('tmp_'):
            #新增的task
            tsk = Task()
        else:
            #修改的task
            tsk = Task.objects.get(id=tskid)
        tsk.name = task['name']
        tsk.progress = task['progress']
        tsk.progressByWorklog = task['progressByWorklog']
        tsk.relevance = task['relevance'] if task.has_key('relevance') else 0
        tsk.type = task['type'] if task.has_key('type') else u''
        tsk.typeId = task['typeId'] if task.has_key('typeId') else u''
        tsk.description = task['description']
        tsk.code = task['code']
        tsk.level = task['level']
        tsk.status = task['status']
        tsk.depends = task['depends']
        tsk.start = int_to_dt(task['start'])
        tsk.duration = task['duration']
        tsk.end = int_to_dt(task['end'])
        tsk.startIsMilestone = task['startIsMilestone']
        tsk.endIsMilestone = task['endIsMilestone']
        tsk.collapsed = task['collapsed'] if task.has_key('collapsed') else False
        tsk.hasChild = task['hasChild'] if task.has_key('hasChild') else False
        tsk.task_order = task_index

        tsk.save()

        gantt_logger(opruid,user,u'任务',tsk.id)

        #assignments
        new_Assig_list=[]
        for assig in assigs:
            if str(assig['id']).startswith(u'tmp_'):
                asi = Assignment()
            else:
                asi = Assignment.objects.get(id = assig['id'])
            asi.task = tsk
            asi.resource = User.objects.get(id = assig['resourceId'])
            asi.role = Role.objects.get(id = assig['roleId'])
            asi.effort = Decimal(assig['effort'])

            asi.save()
            new_Assig_list.append(asi.id)

            gantt_logger(opruid,user, u'任务指派', asi.id)

        tsk_assigs = Assignment.objects.filter(task=tsk)
        for tskasi in tsk_assigs:
            if tskasi.id not in new_Assig_list:
                gantt_logger(opruid,user, u'删除任务指派', tskasi.id)
                tskasi.delete()

    #删除的task
    delids = project['deletedTaskIds']
    # print delids

    for i in delids:
        deltask = Task.objects.get(id=i)
        gantt_logger(opruid,user, u'删除任务', deltask.id)
        deltask.delete()

    return gen_prj_json()

def gen_prj_json(prj_editable=True):
    '''从数据库中生成项目的json数据'''
    res={'tasks':[],'resources':[],'roles':[],'canWrite':prj_editable,'canWriteOnParent':prj_editable,'canDelete':prj_editable}

    #resources
    resources = User.objects.filter(is_superuser=False).order_by("id")
    for resource in resources:
        # 人员姓名采用中国姓名格式
        res['resources'].append({'id':resource.id,'name':resource.username if resource.last_name+resource.first_name==u'' else resource.last_name+resource.first_name})

    #roles
    roles = Role.objects.all().order_by("id")
    for role in roles:
        res['roles'].append({'id':role.id,'name':role.name})

    #tasks
    tasks = Task.objects.all().order_by("task_order")
    for task in tasks:
        prjtsk={'id':task.id,\
                'name':task.name,\
                'progress':task.progress,\
                'progressByWorklog':task.progressByWorklog,\
                'relevance':task.relevance,\
                'type':task.type,\
                'typeId':task.typeId,\
                'description':task.description,\
                'code':task.code,\
                'level':task.level,\
                'status':task.status,\
                'depends':task.depends,\
                'canWrite':True,\
                'start':dt_to_int(str(task.start)[0:19]),\
                'duration':task.duration,\
                'end':dt_to_int(str(task.end)[0:19]),\
                'startIsMilestone':task.startIsMilestone,\
                'endIsMilestone':task.endIsMilestone,\
                'collapsed':task.collapsed,\
                'hasChild':task.hasChild,\
                }

        assigs = Assignment.objects.filter(task=task)
        assig_list=[]
        for assig in assigs:
            #id必须转为字符串，否则task editor的js文件中indexof()方法报错
            assig_list.append({'id':str(assig.id),'resourceId':assig.resource.id,\
                               'roleId':assig.role.id,'effort':round(assig.effort,0)})
        prjtsk['assigs'] = assig_list
        res['tasks'].append(prjtsk)

    return res

def clean_user_session(username):
    '''清除用户会话记录'''
    user = User.objects.get(username = username)

    ses = Session.objects.all()

    if ses:
        for s in ses:
            sdata = s.get_decoded()
            if sdata.has_key('_auth_user_id'):
                if sdata['_auth_user_id'] == str(user.id):
                    s.delete()

def get_write_permission(username):
    '''获取编辑权限，最先加载项目数据的用户将获得编辑权限，
       用户退出登录或者会话超时后释放(直接关闭浏览器无法释放)
    '''
    with transaction.atomic():
        #
        still_hold = False
        # 获取表锁，其他请求将等待资源释放
        handler = GanttLock.objects.select_for_update()
        if handler:
            lockholder = handler[0]
        else:
            # 若不存在初始数据，则创建
            lockholder = GanttLock()
        if not lockholder.user:
            lholder = u''
        else:
            lholder_user = User.objects.get(username=lockholder.user)
            lholder = str(lholder_user.id)
        # 检查会话
        sessions = Session.objects.all()
        for s in sessions:
            sdata = s.get_decoded()
            if sdata.has_key('_auth_user_id'):
                # 若存在该用户的会话，则仍持有编辑锁
                if sdata['_auth_user_id'] == lholder:
                    still_hold = True
            else:
                still_hold = False
        if not lockholder.user or not still_hold:
            lockholder.user = username
            lockholder.save()
            prj_editable = True
        # 若仍持有锁，但持锁者是当前用户
        elif still_hold and (lockholder.user == username):
            prj_editable = True
        else:
            prj_editable = False

        return {'canWrite':prj_editable,'lockmsg':str(lockholder)}

def gantt_logger(opruid,by_user,to_model,to_model_id):
    '''简陋日志记录'''
    try:
        log = GanttLog()
        log.opruid = opruid
        log.user = by_user
        log.to_model = to_model
        log.to_model_id = to_model_id
        log.save()
    except Exception,e:
        print u'记录日志失败：'+repr(e)