from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('StudyGuidelinePortal.urls')),
    path('admin1/', include('AdminPanel.urls')),
]

handler404 = 'StudyGuidelinePortal.views.handle404Error'