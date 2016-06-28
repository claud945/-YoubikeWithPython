# coding=UTF-8
"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
#from blog import views
from blog import views
urlpatterns = [
    url(r'^youbike/(\d+)/(\d+)/$', views.testParemeter), 
    url(r'^youbike/$',views.youbike),
    url(r'^admin/', admin.site.urls),

    #url(r'^drinks/p1(\w+)p2(.+)/$','blog.views.drinks'),
    #第一個參數幾代 #第二個參數集體大小
    url(r'^$', views.youbike, name='youbike'),
]