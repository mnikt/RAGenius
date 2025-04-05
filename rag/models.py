from django.contrib.auth.models import User
from django.db import models


class DirectoryModel(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class FileModel(models.Model):
    # file = models.FileField(upload_to='files')
    name = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    directory = models.ForeignKey(DirectoryModel, on_delete=models.CASCADE)
