from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path
from sitebase import views

urlpatterns = [

    url(r'^$', views.Index.as_view(), name='home'),
    url(r'^calendar$', views.Calendar.as_view(), name='calendar'),
    url(r'^jsoncal', views.JsonCalendar.as_view(), name='calendarJSON'),

    # url(
    #     r'^password_reset/$',
    #     auth_views.PasswordResetView,
    #     name='password_reset'
    # ),
    # url(
    #     r'^password_reset/done/$',
    #     auth_views.PasswordResetDoneView,
    #     name='password_reset_done'
    # ),
    # url(
    #     r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.PasswordResetConfirmView,
    #     name='password_reset_confirm'
    # ),
    # url(
    #     r'^reset/done/$',
    #     auth_views.PasswordResetCompleteView,
    #     name='password_reset_complete'
    # ),
]
