from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('jet/', include('jet.urls')),  # без namespace!
    path('admin/', admin.site.urls),
    path('', include('Alfa_repair_app.urls')),
]