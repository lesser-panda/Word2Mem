from django import forms

from wordbook.models import Word, VocabularyCollection, Memory


class VocabularyCollectionForm(forms.ModelForm):
    class Meta:
        model = VocabularyCollection
        fields = '__all__'

        def clean_name(self):
            return self.cleaned_data['name'].strip()

        def clean_category(self):
            return self.cleaned_data['category'].strip()
