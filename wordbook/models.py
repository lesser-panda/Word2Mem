from datetime import datetime

from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse
import uuid

from csvs.validator import validate_file_size


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
        return self.user.username+' '+self.name

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="words", null=True, editable=False)
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

    def __str__(self):
        try:
            return self.user.username + ' ' + self.word
        except AttributeError:
            return self.word

    @property
    def last_correct_date(self):
        return self.histories.filter(correctness=True).latest('datetime').datetime

    @property
    def last_incorrect_date(self):
        return self.histories.filter(correctness=False).latest('datetime').datetime

    @property
    def correct_count(self):
        return self.histories.filter(correctness=True).count()

    @property
    def incorrect_count(self):
        return self.histories.filter(correctness=False).count()

    class Meta:
        ordering = ['word']


class History(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    word = models.ForeignKey(Word, related_name='histories', on_delete=models.SET_NULL, null=True)
    history_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="histories", null=True, editable=False)
    correctness = models.BooleanField()
    datetime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        try:
            return self.user.username+' '+self.word.word+' '+str(self.correctness)
        except AttributeError:
            return self.user.username+' USER_DELETED_WORD '+str(self.correctness)

    class Meta:
        ordering = ['datetime']
