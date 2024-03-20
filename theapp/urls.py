
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.http import FileResponse
import os

def serve_service_worker(request):
    service_worker_path = os.path.join(settings.BASE_DIR, 'serviceworker.js')
    return FileResponse(open(service_worker_path, 'rb'))


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('social/', include('social.urls')),
    path('lawyers/', include('lawyers.urls')),
    # call counseling
    path('social/call-counseling/', include('social.call_counseling.urls') ),
    # online counseling
    path('social/online-counseling/', include('social.online_counseling.urls') ),
    path('serviceworker.js', serve_service_worker, name='serve_service_worker'),

]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)