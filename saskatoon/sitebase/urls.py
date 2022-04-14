from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, re_path
from sitebase import views

urlpatterns = [

    url(r'^$', views.Index.as_view(), name='home'),
    re_path(r'^calendar/$', views.Calendar.as_view(), name='calendar'),
    url(r'^jsoncal', views.JsonCalendar.as_view(), name='calendarJSON'),

    path('reset_password/',
         auth_views.PasswordResetView.as_view(),
         name ='reset_password'),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(),
         name ='password_reset_done'),

    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(),
         name ='password_reset_confirm'),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name ='password_reset_complete'),

]
