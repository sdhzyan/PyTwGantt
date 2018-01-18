# PyTwGantt
Django APP base on TwGantt.

PyTwGantt是一个基于JQuery Gantt editor插件开发的Django APP,目的是提供网页版甘特图编辑、展示功能。目前只简陋地实现了单项目、单人编辑功能（不支持并发编辑）

1.环境

python 2.7、Django 1.11.7以及前端插件Gantt editor(http://roberto.open-lab.com/2012/08/24/jquery-gantt-editor/)

2.安装

安装前检查APP文件夹名是否为TwGantt,若为PyTwGantt，请先改名。

step 1. 在你的Django项目setting.py中配置INSTALLED_APPS,添加 'TwGantt'

step 2. 在你的Django项目urls.py中'from django.conf.urls import url'后添加',include'

step 3. 在你的Django项目urls.py中配置urlpatterns,添加 url(r'^TwGantt/', include("TwGantt.urls"))

step 4. 使用makemigrations及migrate把models同步到数据库中

3.测试

运行开发测试服务器 manage.py runserver, 点击 http://127.0.0.1:8000/TwGantt

4.开发

按需重写models及views

更新说明:

2018-01-18

添加简单的日志功能

2018-01-17

基于session及GanttLock表控制编辑，获得编辑锁的用户才能编辑项目数据，最早打
开项目的用户将获取编辑锁，其他用户以只读方式打开，锁持有者退出登录或会话超时
（每个会话有效时长为1小时）将释放编辑锁，直接关闭浏览器无法正常释放锁。

2018-01-12

汉化v1.1

2018-01-09

单项目单人编辑版本v1.0

