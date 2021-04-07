from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser, User
from .validator import validate_file_size


# Create your models here.


class Csv(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="csv", null=True, editable=False)
    file_name = models.FileField(upload_to='csvs', validators=[validate_file_size])

    def __str__(self):
        return f"File id: {self.id}"
