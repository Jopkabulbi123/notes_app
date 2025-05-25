from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Note, Category
from .forms import NoteForm, NoteFilterForm
from django.contrib.auth import authenticate, login
from .forms import RegisterForm
from django.contrib.auth import login

@login_required
def note_create(request):
    if not Category.objects.exists():
        Category.objects.create(title="Загальне")
        messages.info(request, "Автоматично створено категорію 'Загальне'")

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user

            if not note.category:
                note.category = Category.objects.first()
                messages.info(request, f"Нотатку автоматично віднесено до категорії '{note.category}'")

            note.save()
            messages.success(request, f"Нотатку '{note.title}' успішно збережено!")
            return redirect('note_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Помилка у полі '{field}': {error}")
    else:
        form = NoteForm()

    return render(request, 'notes/note_form.html', {
        'form': form,
        'title': 'Створення нотатки'
    })


@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, f"Нотатку '{note.title}' успішно оновлено!")
            return redirect('note_detail', pk=note.pk)
    else:
        form = NoteForm(instance=note)
    return render(request, 'notes/note_form.html', {
        'form': form,
        'object': note,
        'title': 'Редагування нотатки'
    })


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = reverse_lazy('note_list')
    template_name = 'notes/note_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user)
        form = NoteFilterForm(self.request.GET)

        if form.is_valid():
            category = form.cleaned_data.get('category')
            search = form.cleaned_data.get('search')

            if category:
                queryset = queryset.filter(category=category)

            if search:
                queryset = queryset.filter(title__icontains=search)

        return queryset.select_related('category').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = NoteFilterForm(self.request.GET)
        return context


def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('note_list')
        else:
            messages.error(request, "Невірний логін або пароль")
            return redirect('login')

    return render(request, 'registration/login.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            Category.objects.create(title="Робота", user=user)
            Category.objects.create(title="Особисте", user=user)
            Category.objects.create(title="Покупки", user=user)

            login(request, user)
            messages.success(request, "Ви успішно зареєструвалися!")
            return redirect('note_list')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})