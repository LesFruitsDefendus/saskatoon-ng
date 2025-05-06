from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from sitebase import views

urlpatterns = [
    url(r'^$',
        views.Index.as_view(),
        name='home'),

    url('terms_conditions/',
        views.TermsConditionsView.as_view(),
        name='terms_conditions'),

    url(r'^jsoncal',
        views.JsonCalendar.as_view(),
        name='calendarJSON'),

    re_path(r'^calendar/$',
            views.Calendar.as_view(),
            name='calendar'),

    path('equipment_points/',
         views.EquipmentPointsPDFView.as_view(),
         name='equipment-points'),

    path('privacy_policy/',
         views.PrivacyPolicyView.as_view(),
         name='privacy_policy'),

    path('volunteer_waiver/',
         views.VolunteerWaiverPDFView.as_view(),
         name='volunteer-waiver'),

    path('reset_password/',
         auth_views.PasswordResetView.as_view(),
         name='reset_password'),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
