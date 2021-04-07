from django.contrib import admin

# Register your models here.
from wordbook.models import VocabularyCollection, Word, Memory

admin.site.register(VocabularyCollection)
admin.site.register(Word)
admin.site.register(Memory)
