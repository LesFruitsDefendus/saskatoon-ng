from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path
from sitebase import views

urlpatterns = [

    # The home page
    url(r'^$', views.index, name='index'),
    path('accounts/login/', auth_views.LoginView.as_view()),
    path('i18n/', include('django.conf.urls.i18n')),
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
    url(
        r'^calendar$',
        views.Calendar.as_view(),
        name='calendar'
    ),
    url(
        r'^jsoncal',
        views.JsonCalendar.as_view(),
        name='calendarJSON'
    ),
]
