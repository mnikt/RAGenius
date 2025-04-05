from django.urls import path
from .views import home, files, file_delete

urlpatterns = [
    path('', home, name='home'),
    path('files/', files, name='files'),
    path('files/delete/<int:file_id>/', file_delete, name='delete_file'),
]