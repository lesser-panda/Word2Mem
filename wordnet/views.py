from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from wordnet.forms import DictionarySearchForm

from nltk.corpus import wordnet as wn
from PyDictionary import PyDictionary


@login_required
def search(request):

    # if user pressed "Add to Vocabulary Collection" button,
    # then create a Vocabulary Collection named something like
    # "From Dictionary Search" (check if table exist first)
    # and add the searched word into that Vocabulary Collection
    def add_to_db(spelling, definition):
        vc, table_exist = request.user.vc_list.get_or_create(name="From Dictionary Search", category="English")
        word_record, word_exist = vc.words.get_or_create(word=spelling, definition=definition, user_id=request.user.id)

    # check if word is already in
    # user's "From Dictionary Search" Vocabulary Collection
    def already_in_db(spelling):
        vc, table_exist = request.user.vc_list.get_or_create(name="From Dictionary Search", category="English")
        count = vc.words.filter(word=spelling).count()
        if count == 0:
            return False
        else:
            return True

    # if user pressed "Add to Vocabulary Collection" button:
    if request.method == 'POST' and 'add_word' in request.POST:
        response = request.POST.get('definition')
        word = request.POST.get('word')
        # add Word to Vocabulary Collection named "From Dictionary Search"
        add_to_db(spelling=word, definition=response)
        # need an empty Form otherwise the search bar would disappear
        search_form = DictionarySearchForm(None)
        # just so the page appears to be never refreshed!
        context = {'exist': False,
                   'response': response,
                   'search_form': search_form,
                   'just_added': True}
        return render(request, 'wordnet/search.html', context=context)

    # normal searching from users
    search_form = DictionarySearchForm(request.POST or None)
    context = {'search_form': search_form}
    if search_form.is_valid():
        dictionary = PyDictionary()
        word = search_form.cleaned_data['search_term']
        # check if word is already in
        # user's "From Dictionary Search" Vocabulary Collection
        in_db = already_in_db(word)
        context["in_db"] = in_db
        meaning = dictionary.meaning(word)
        if type(meaning) == dict:
            context["exist"] = True
            context["word"] = word
            context["response"] = str(meaning).replace("{", "").replace("}", "")
        else:
            context["exist"] = False
            context["response"] = "Term not found in WordNet!"
        return render(request, 'wordnet/search.html', context=context)
    return render(request, 'wordnet/search.html', context=context)
