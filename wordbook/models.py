from datetime import datetime

from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse
import uuid


class VocabularyCollection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vc_list", null=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    vc_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, unique=False)
    category = models.CharField(max_length=45)
    add_date = models.DateField(default=datetime.now, blank=True, editable=False)
    last_accessed = models.DateField(null=True, blank=True, editable=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('wordbook_vocabulary_list_detail_urlpattern',
                       kwargs={'uuid': self.uuid})

    def get_update_url(self):
        return reverse('wordbook_vocabulary_update_urlpattern',
                       kwargs={'uuid': self.uuid})

    class Meta:
        ordering = ['add_date', 'name']
        constraints = [
            UniqueConstraint(fields=['user', 'name', 'category'],
                             name='unique_vocabulary_collection')
        ]


class Word(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="word", null=True, editable=False)
    vocabulary_collection = models.ForeignKey(VocabularyCollection, related_name='words', on_delete=models.CASCADE)
    word_id = models.AutoField(primary_key=True)
    # Why unique=False for the column 'word'?
    # I want to allow duplicated word in the Word table
    # so that for words that shares the same spelling
    # in different languages (e.g 'student' in English and German)
    # users can have two records of 'student'
    # each with a different definition
    # The drawback is that there could be duplicated records,
    # but so far this is what I can do.
    word = models.CharField(max_length=45, unique=False)
    definition = models.TextField()
    # language = models.CharField(max_length=45, blank=True, default='English')

    def __str__(self):
        return self.word

    # need testing!
    def get_absolute_url(self):
        return reverse('wordbook_worddefinition_urlpattern',
                       kwargs={'uuid': self.uuid})

    class Meta:
        ordering = ['word']


class Memory(models.Model):
    # uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    word = models.OneToOneField(Word, related_name='memories', on_delete=models.CASCADE)
    memory_id = models.AutoField(primary_key=True)
    # word_id = models.ForeignKey(Word, related_name='memories', on_delete=models.CASCADE, primary_key=True)
    correct_count = models.IntegerField(blank=True, default=0)
    incorrect_count = models.IntegerField(blank=True, default=0)
    last_correct = models.DateField(default=datetime.now, blank=True)
    last_incorrect = models.DateField(default=datetime.now, blank=True)
    # first_correct = models.DateField(default=datetime.now, blank=True)

    def __str__(self):
        return self.word.word

    class Meta:
        ordering = ['correct_count']
