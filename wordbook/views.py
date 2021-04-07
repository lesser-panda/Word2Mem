from datetime import datetime

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import DeleteView

from wordbook.forms import VocabularyCollectionForm
from wordbook.models import VocabularyCollection, Word, Memory
from wordbook.utils import ObjectCreateMixin



class Homepage(View):

    def get(self, request):
        return render(request, "wordbook/home.html", {})


class VocabularyCollectionList(View):

    def get(self, request):
        request.user.vc_list.get_or_create(name="From Dictionary Search", category="English")
        return render(request,
                      'wordbook/word_collection.html',
                      {'collection_list': request.user.vc_list.all(),})


class VocabularyCollectionDetail(View):
    page_kwarg = 'page'
    paginate_by = 25

    def get(self, request, uuid):
        vocabulary_collection = get_object_or_404(
            VocabularyCollection,
            uuid=uuid
        )
        if vocabulary_collection in request.user.vc_list.all():
            word_list = vocabulary_collection.words.all()

            paginator = Paginator(
                word_list,
                self.paginate_by
            )
            page_number = request.GET.get(
                self.page_kwarg
            )
            try:
                page = paginator.page(page_number)
            except PageNotAnInteger:
                page = paginator.page(1)
            except EmptyPage:
                page = paginator.page(
                    paginator.num_pages)
            if page.has_previous():
                prev_url = "?{pkw}={n}".format(
                    pkw=self.page_kwarg,
                    n=page.previous_page_number())
            else:
                prev_url = None
            if page.has_next():
                next_url = "?{pkw}={n}".format(
                    pkw=self.page_kwarg,
                    n=page.next_page_number())
            else:
                next_url = None

            page_list = []
            for i in range(0, paginator.num_pages):
                page_list.append(i+1)

            return render(
                request,
                'wordbook/word_collection_detail.html',
                {'vocabulary_collection': vocabulary_collection,
                 'word_list': page,
                 'is_paginated': page.has_other_pages(),
                 'paginator': paginator,
                 'previous_page_url': prev_url,
                 'next_page_url': next_url,
                 'page_list': page_list,
                 }
            )
        return render(request, "wordbook/home.html", {})

    # 这玩意儿本来是不需要post的，但是flashcard最后一个单词，post form的时候
    # 总得跳转到一个不是flashcard的页面（因为退出了）
    # 所以暂时设定flashcard跑完跳转到这里
    # 这个post就是为了接个盘，之后把sql操作写这里
    def post(self, request, *args, **kwargs):
        print(kwargs)
        print("User answered the flashcard!")
        print(request.POST.get('word'))
        print("word_id:")
        print(request.POST.get('word_uuid'))

        word = Word.objects.get(uuid=request.POST.get('word_uuid'))
        try:
            memory = word.memories
        except:
            print("memory not exist! creating new memory")
            memory = Memory(word=word)

        print("correctness:")
        print(request.POST.get('correctness'))
        if int(request.POST.get('correctness')) == 0:
            memory.incorrect_count += 1
            memory.last_incorrect = datetime.now()
        elif int(request.POST.get('correctness')) == 1:
            memory.correct_count += 1
            memory.last_correct = datetime.now()

        memory.save()

        cache.delete('word_list')

        return self.get(request, kwargs["uuid"])


class VocabularyCollectionListCreate(ObjectCreateMixin, View):

    form_class = VocabularyCollectionForm
    template_name = 'wordbook/word_collection_create.html'


def vocabularycollection_remove(request, uuid):
    vocabulary_collection = get_object_or_404(VocabularyCollection, uuid=uuid)
    vocabulary_collection.delete()
    return HttpResponseRedirect('/vocab_list/')


def word_remove(request, uuid):
    word = get_object_or_404(Word, uuid=uuid)
    currernt_link = word.vocabulary_collection.get_absolute_url()
    word.delete()
    return HttpResponseRedirect(currernt_link)


class WordDefinition(View):

    def get(self, request, uuid):
        word = get_object_or_404(
            Word,
            uuid=uuid
        )
        memory = word.memories
        return render(request,
                      'wordbook/word_definition.html',
                      {'word': word,
                       'memory': memory})


class FlashCard(View):

    def get(self, request, uuid, r_card_num):

        vocabulary_collection = get_object_or_404(
            VocabularyCollection,
            uuid=uuid
        )

        if r_card_num == 1:
            cache.delete('word_list')
        word_list = cache.get('word_list')
        if not word_list:
            word_list = vocabulary_collection.words.all().order_by("?")
            cache.set('word_list', word_list)

        p = Paginator(word_list, 1)

        try:
            card = p.page(r_card_num)
        except EmptyPage:
            print("card num out of bound")
            card = p.page(1)

        return render(
            request,
            'wordbook/flashcard.html',
            {'vocabulary_collection': vocabulary_collection,
             'card': card}
        )

    def post(self, request, *args, **kwargs):
        print(kwargs)
        print("User answered the flashcard!")
        print(request.POST.get('word'))
        print("word_id:")
        print(request.POST.get('word_uuid'))

        word = Word.objects.get(uuid=request.POST.get('word_uuid'))
        try:
            memory = word.memories
        except:
            print("memory not exist! creating new memory")
            memory = Memory(word=word)

        print("correctness:")
        print(request.POST.get('correctness'))
        if int(request.POST.get('correctness')) == 0:
            memory.incorrect_count += 1
            memory.last_incorrect = datetime.now()
        elif int(request.POST.get('correctness')) == 1:
            memory.correct_count += 1
            memory.last_correct = datetime.now()

        vc = word.vocabulary_collection
        vc.last_accessed = datetime.now()
        vc.save()

        memory.save()

        return self.get(request, kwargs["uuid"], kwargs["r_card_num"])
