from django import forms


class DictionarySearchForm(forms.Form):
    search_term = forms.CharField()
