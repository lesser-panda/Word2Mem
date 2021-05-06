from collections import OrderedDict
from datetime import datetime, date
from operator import itemgetter

from django.db.models import Count
from django.db.models.functions import ExtractWeekDay, TruncDate
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.views.generic import UpdateView

from wordbook.forms import VocabularyCollectionForm
from wordbook.models import VocabularyCollection, Word, History
from wordbook.utils import ObjectCreateMixin
from .fusioncharts import FusionCharts


class Homepage(View):

    def get(self, request):
        return render(request, "wordbook/home.html", {})


class VocabularyCollectionList(View):

    def get(self, request):
        request.user.vc_list.get_or_create(name="From Dictionary Search", category="English")
        return render(request,
                      'wordbook/word_collection.html',
                      {'collection_list': request.user.vc_list.all(), })


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
                page_list.append(i + 1)

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

        if int(request.POST.get('correctness')) == 0:
            correctness = False
        else:
            correctness = True

        new_record = History(word=word,
                             datetime=datetime.now(),
                             user_id=request.user.id,
                             correctness=correctness)
        new_record.save()

        vc = word.vocabulary_collection
        vc.last_accessed = datetime.now()
        vc.save()

        cache_label = 'word_list' + str(request.user.id)

        cache.delete(cache_label)

        return self.get(request, kwargs["uuid"])


class VocabularyCollectionListCreate(ObjectCreateMixin, View):
    form_class = VocabularyCollectionForm
    template_name = 'wordbook/word_collection_create.html'


class VocabularyCollectionUpdate(UpdateView):
    form_class = VocabularyCollectionForm
    model = VocabularyCollection
    template_name = 'wordbook/word_collection_update.html'

    def get_object(self, queryset=None):
        return VocabularyCollection.objects.get(uuid=self.kwargs.get("uuid"))


def vocabularycollection_remove(request, uuid):
    vocabulary_collection = get_object_or_404(VocabularyCollection, uuid=uuid)
    vocabulary_collection.delete()
    return HttpResponseRedirect('/vocab_list/')


def word_remove(request, uuid):
    word = get_object_or_404(Word, uuid=uuid)
    currernt_link = word.vocabulary_collection.get_absolute_url()
    word.delete()
    return HttpResponseRedirect(currernt_link)


class FlashCard(View):

    def get(self, request, uuid, r_card_num):

        vocabulary_collection = get_object_or_404(
            VocabularyCollection,
            uuid=uuid
        )

        cache_label = 'word_list' + str(request.user.id)

        if r_card_num == 1:
            cache.delete(cache_label)
        word_list = cache.get(cache_label)
        if not word_list:
            word_list = vocabulary_collection.words.all().order_by("?")
            cache.set(cache_label, word_list)

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

        if int(request.POST.get('correctness')) == 0:
            correctness = False
        else:
            correctness = True

        new_record = History(word=word,
                             datetime=datetime.now(),
                             user_id=request.user.id,
                             correctness=correctness)
        new_record.save()

        print("correctness:")
        print(request.POST.get('correctness'))

        vc = word.vocabulary_collection
        vc.last_accessed = datetime.now()
        vc.save()

        return self.get(request, kwargs["uuid"], kwargs["r_card_num"])


class StatisticsView(View):

    def get(self, request):
        context = {}
        context['vc_count'] = VocabularyCollection.objects.filter(user_id=request.user.id).count()
        context['word_count'] = Word.objects.filter(user_id=request.user.id).count()
        context['online_days'] = History.objects.filter(user_id=request.user.id).dates('datetime', 'day').count()

        pieData = OrderedDict()
        pieData["data"] = []
        pieData["data"].append({"label": '✓',
                                "value": History.objects.filter(user_id=request.user.id, correctness=True).count()})
        pieData["data"].append({"label": 'X',
                                "value": History.objects.filter(user_id=request.user.id, correctness=False).count()})
        pieChartConfig = OrderedDict()
        pieChartConfig["caption"] = "Historical Performance"
        pieChartConfig["showLegend"] = 0
        pieChartConfig["theme"] = "fusion"
        pieData["chart"] = pieChartConfig

        pieChart = FusionCharts("pie2d", "correctnessPieChart", "100%", "100%", "correctnessPie-container", "json",
                                pieData)
        context["piechart_output"] = pieChart.render()

        current_week = date.today().isocalendar()[1]
        weekdayData = History.objects \
            .filter(user_id=request.user.id, datetime__week=current_week) \
            .annotate(label=ExtractWeekDay("datetime"), order=ExtractWeekDay("datetime"))\
            .order_by() \
            .values('label', 'order').annotate(value=Count("uuid"))

        weekdayData = list(weekdayData)

        weekdayStr = {1: "Sunday",
                      2: "Monday",
                      3: "Tuesday",
                      4: "Wednesday",
                      5: "Thursday",
                      6: "Friday",
                      7: "Saturday"}
        missingDays = [1, 2, 3, 4, 5, 6, 7]
        for d in weekdayData:
            missingDays.remove(d['label'])
            d['label'] = weekdayStr[d["label"]]
        for d in missingDays:
            weekdayData.append({'label': weekdayStr[d], 'value': 0, 'order': d})

        print(weekdayData)

        weekdayData = sorted(weekdayData, key=itemgetter('order'))

        weekdayBarData = OrderedDict()
        weekdayBarData["data"] = weekdayData
        weekdayBarConfig = OrderedDict()
        weekdayBarConfig["caption"] = "Number of words studied this week"
        weekdayBarConfig["theme"] = "fusion"
        weekdayBarConfig["showLabel"] = 1
        weekdayBarData["chart"] = weekdayBarConfig
        weekdayBarChart = FusionCharts("column2d", "weekdayBarChart", "100%", "100%", "weekdayBar-container", "json",
                                       weekdayBarData)
        context["weekdaybar_output"] = weekdayBarChart.render()

        return render(request,
                      'wordbook/statistics.html',
                      context)
