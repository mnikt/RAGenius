from django.contrib import admin
from .models import FileModel, DirectoryModel

# Register your models here.
@admin.register(DirectoryModel)
class DirectoryAdmin(admin.ModelAdmin):
    pass


@admin.register(FileModel)
class FileAdmin(admin.ModelAdmin):
    pass
