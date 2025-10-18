from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from saskatoon.settings import DEBUG, MEDIA_URL, MEDIA_ROOT
import debug_toolbar

urlpatterns = [
    path('', include('sitebase.urls')),
    path('', include('member.urls')),
    path('', include('harvest.urls')),
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('rosetta/', include('rosetta.urls'))
]

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT) # type: ignore

handler400 = 'sitebase.views.handler400'
handler403 = 'sitebase.views.handler403'
handler404 = 'sitebase.views.handler404'
handler500 = 'sitebase.views.handler500'
