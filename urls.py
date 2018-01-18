#-*- coding:utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.return_home,name='home'),
    url(r'^saveprj/', views.save_prj),
    url(r'^loadprj/', views.load_prj),
    url(r'^login/', views.user_login,name='login'),
    url(r'^logout/', views.user_logout,name='logout'),
]