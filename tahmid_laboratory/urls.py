from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Tahmid Laboratory Admin"
admin.site.site_title = "Tahmid Laboratory"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('lab.urls')),
]