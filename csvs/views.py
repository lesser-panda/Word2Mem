from django.contrib import messages
from django.shortcuts import render

from wordbook.models import Word
from .forms import CsvModelForm
import pandas as pd
import os

# Create your views here.


def upload_file_view(request, **kwargs):
    form = CsvModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        new_file = form.save()
        form = CsvModelForm()
        request.user.csv.all().delete()
        request.user.csv.add(new_file)
        # The CSV table of each user is cleaned
        # every time the user uploads a new .csv file
        # and therefore, the following .get() function
        # will ALWAYS get only ONE csv file
        obj = request.user.csv.get()
        try:
            df = pd.read_csv(obj.file_name.path)
            df.columns = df.columns.str.strip()
            df.columns = df.columns.str.lower()
            df_records = df.to_dict('records')
            model_instances = [Word(
                user_id=request.user.id,
                vocabulary_collection=request.user.vc_list.get(uuid=kwargs['uuid']),
                word=record['word'],
                definition=record['definition'],
            ) for record in df_records]
            request.user.word.bulk_create(model_instances)
            os.remove(obj.file_name.path)
            request.user.csv.all().delete()
            messages.success(request, 'vocabularies imported successfully!')
        except:
            os.remove(obj.file_name.path)
            request.user.csv.all().delete()
            messages.error(request, 'Error! Please check your csv file. Make sure it is a correct CSV file with columns "Word" and "Definition"')

    return render(request, 'csvs/upload.html', {'form': form, 'uuid': kwargs['uuid']})
