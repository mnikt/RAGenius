import logging

from django.contrib.auth.models import User
from django.db import models


from rag.rag import delete_corpus, create_corpus, upload_file, delete_file


class DirectoryModel(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    corpus = models.CharField(max_length=300)

    def delete(self, *args, **kwargs):
        logging.info(f"Deleting directory: {self.name}")

        delete_corpus(self.corpus)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            logging.info(f"Created new object: {self.name}")
            corp = create_corpus(f'{self.owner.id}-{self.name}')
            self.corpus = corp
            self.save()


class FileModel(models.Model):
    name = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    directory = models.ForeignKey(DirectoryModel, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        logging.info(f"Deleting file: {self.name}")
        delete_file(self)
        super().delete(*args, **kwargs)
