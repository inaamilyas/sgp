from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('StudyGuidelinePortal.urls')),
    path('admin1/', include('AdminPanel.urls')),
]

handler404 = 'StudyGuidelinePortal.views.handle404Error'