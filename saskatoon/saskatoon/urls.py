from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from django.conf import settings

urlpatterns = [
    path('', include('sitebase.urls')),
    path('', include('member.urls')),
    path('', include('harvest.urls')),
    path('',include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('rosetta/', include('rosetta.urls'))
]

