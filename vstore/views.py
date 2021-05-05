from django.contrib import messages
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views import View
from django.views.generic import ListView
import pandas as pd

from vstore.models import StoreItem
from wordbook.models import Word


class StoreView(ListView):
    model = StoreItem
    template_name = 'vstore/vocab_store.html'


class StoreItemDetail(View):

    def get(self, request, id):
        store_item = get_object_or_404(
            StoreItem,
            id=id
        )

        return render(
            request,
            'vstore/storeitem_detail.html',
            {'store_item': store_item,
             }
        )

    def post(self, request, id):
        store_item = get_object_or_404(
            StoreItem,
            id=id
        )

        obj, created = request.user.vc_list.get_or_create(name=store_item.name, category=store_item.category)
        if not created:
            messages.error(request, 'A vocabulary collection with the same name and category is already in your account!')
        else:
            try:
                df = pd.read_csv(store_item.file_name.path)
                df.columns = df.columns.str.strip()
                df.columns = df.columns.str.lower()
                df_records = df.to_dict('records')
                model_instances = [Word(
                    user_id=request.user.id,
                    vocabulary_collection=obj,
                    word=record['word'],
                    definition=record['definition'],
                ) for record in df_records]
                request.user.words.bulk_create(model_instances)
                messages.success(request, 'Vocabularies added to your account!')
            except:
                messages.error(request,
                               'Error while adding this vocabulary collection')
        return render(
            request,
            'vstore/storeitem_detail.html',
            {'store_item': store_item,
             'just_added': True,
             }
        )
