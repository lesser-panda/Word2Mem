from django.db import models

# Create your models here.
from django.urls import reverse

from csvs.validator import validate_file_size


class StoreItem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, unique=False)
    category = models.CharField(max_length=45)
    description = models.TextField()
    file_name = models.FileField(upload_to='store', validators=[validate_file_size])

    def __str__(self):
        return self.name + " (" + self.category + ")"

    def get_absolute_url(self):
        return reverse('vstore:store_item_detail_urlpattern',
                       kwargs={'id': self.id})
