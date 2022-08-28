from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static


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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'sitebase.views.handler400'
handler403 = 'sitebase.views.handler403'
handler404 = 'sitebase.views.handler404'
handler500 = 'sitebase.views.handler500'
