from django.urls import path
from .views import upload_file_view


app_name='csvs'

urlpatterns = [
    path('upload_csv/<uuid:uuid>', upload_file_view, name='upload_csv_urlpattern'),
]