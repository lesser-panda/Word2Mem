# /wordbook/urls.py
from django.urls import path, include

from csvs.views import upload_file_view
from . import views
from .views import VocabularyCollectionList, Homepage, VocabularyCollectionListCreate, \
    VocabularyCollectionDetail, FlashCard, vocabularycollection_remove, word_remove, VocabularyCollectionUpdate

urlpatterns = [
    path('', Homepage.as_view(), name='wordbook_homepage_urlpattern'),
    path('vocab_list/', VocabularyCollectionList.as_view(), name='wordbook_vocabulary_list_urlpattern'),
    path('vocab_list/create/', VocabularyCollectionListCreate.as_view(), name='wordbook_vocabulary_list_create_urlpattern'),
    path('vocab_list/<uuid:uuid>', VocabularyCollectionDetail.as_view(), name='wordbook_vocabulary_list_detail_urlpattern'),
    path('vocab_list/<uuid:uuid>/edit/', VocabularyCollectionUpdate.as_view(), name='wordbook_vocabulary_update_urlpattern'),
    path('flashcard/<uuid:uuid>/<int:r_card_num>', FlashCard.as_view(), name='wordbook_flashcard_urlpattern'),
    # path('upload_csv/<uuid:uuid>', upload_file_view, name='upload_csv_urlpattern'),
    path('vocab_list/<uuid:uuid>/delete/', vocabularycollection_remove, name='wordbook_vocabulary_list_delete_urlpattern'),
    path('word/<uuid:uuid>/delete/', word_remove, name='wordbook_word_delete_urlpattern'),
]
