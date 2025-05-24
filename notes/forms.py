from django import forms
from .models import Note, Category

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'text', 'category', 'reminder']

class NoteFilterForm(forms.Form):
    search = forms.CharField(required=False, label='Пошук')
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Категорія'
    )