from django.urls import path
from .views import home, files, file_delete, directory_delete, directory_create, query

urlpatterns = [
    path('', home, name='home'),
    path('files/', files, name='files'),
    path('chat/', query, name='query'),
    path('files/delete/<int:file_id>/', file_delete, name='delete_file'),
    path('directory/', directory_create, name='directory_create'),
    path('files/delete/<int:file_id>/', directory_delete, name='directory_create'),
]