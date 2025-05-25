from django import forms
from .models import Note, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'text', 'category', 'reminder']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'reminder': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'category': 'Категорія',
            'reminder': 'Нагадування',
        }

class NoteFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Пошук',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Пошук по заголовку...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Категорія',
        empty_label="Всі категорії",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }