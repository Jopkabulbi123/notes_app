from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Note, Category
from .forms import NoteForm, NoteFilterForm, RegisterForm
from django.contrib.auth import authenticate, login
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

async def get_object_or_404_async(model, **kwargs):
    return await sync_to_async(get_object_or_404)(model, **kwargs)


async def form_valid_async(form, request, note=None):
    if await sync_to_async(form.is_valid)():
        note = await sync_to_async(form.save)(commit=False)
        note.user = request.user

        if not note.category:
            note.category = await Category.objects.afirst()
            await sync_to_async(messages.info)(request, f"Нотатку автоматично віднесено до категорії '{note.category}'")

        await sync_to_async(note.save)()
        await sync_to_async(messages.success)(request, f"Нотатку '{note.title}' успішно збережено!")
        return True, note
    else:
        for field, errors in form.errors.items():
            for error in errors:
                await sync_to_async(messages.error)(request, f"Помилка у полі '{field}': {error}")
        return False, None


@sync_to_async
def get_form_context(form, object=None, title=None):
    return {
        'form': form,
        'object': object,
        'title': title
    }


@login_required
async def note_create(request):
    if not await Category.objects.aexists():
        await Category.objects.acreate(title="Загальне", user=request.user)
        await sync_to_async(messages.info)(request, "Автоматично створено категорію 'Загальне'")

    if request.method == 'POST':
        form = NoteForm(request.POST)
        is_valid, note = await form_valid_async(form, request)
        if is_valid:
            return redirect('note_list')
    else:
        form = NoteForm()

    context = await get_form_context(form, title='Створення нотатки')
    return await sync_to_async(render)(request, 'notes/note_form.html', context)


@login_required
async def note_detail(request, pk):
    note = await get_object_or_404_async(Note, pk=pk, user=request.user)
    return await sync_to_async(render)(request, 'notes/note_detail.html', {'note': note})


@login_required
async def note_edit(request, pk):
    note = await get_object_or_404_async(Note, pk=pk, user=request.user)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        is_valid, note = await form_valid_async(form, request, note)
        if is_valid:
            return redirect('note_detail', pk=note.pk)
    else:
        form = NoteForm(instance=note)

    context = await get_form_context(form, note, 'Редагування нотатки')
    return await sync_to_async(render)(request, 'notes/note_form.html', context)


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = reverse_lazy('note_list')
    template_name = 'notes/note_confirm_delete.html'

    async def get_queryset(self):
        return await sync_to_async(super().get_queryset)().filter(user=self.request.user)


class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

    async def get_queryset(self):
        queryset = await sync_to_async(Note.objects.filter)(user=self.request.user)
        form = NoteFilterForm(self.request.GET)

        if await sync_to_async(form.is_valid)():
            category = form.cleaned_data.get('category')
            search = form.cleaned_data.get('search')

            if category:
                queryset = await sync_to_async(queryset.filter)(category=category)
            if search:
                queryset = await sync_to_async(queryset.filter)(title__icontains=search)

        return await sync_to_async(queryset.select_related('category').order_by)('-created_at')

    async def get_context_data(self, **kwargs):
        context = await sync_to_async(super().get_context_data)(**kwargs)
        context['filter_form'] = NoteFilterForm(self.request.GET)
        return context


async def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = await sync_to_async(authenticate)(request, username=username, password=password)

        if user is not None:
            await sync_to_async(login)(request, user)
            return redirect('note_list')
        else:
            await sync_to_async(messages.error)(request, "Невірний логін або пароль")
            return redirect('login')

    return await sync_to_async(render)(request, 'registration/login.html')


async def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if await sync_to_async(form.is_valid)():
            user = await sync_to_async(form.save)()

            User = await sync_to_async(get_user_model)()
            categories = [
                Category(title="Робота", user=user),
                Category(title="Особисте", user=user),
                Category(title="Покупки", user=user)
            ]
            await Category.objects.abulk_create(categories)

            await sync_to_async(login)(request, user)
            await sync_to_async(messages.success)(request, "Ви успішно зареєструвалися!")
            return redirect('note_list')
    else:
        form = RegisterForm()

    return await sync_to_async(render)(request, 'registration/register.html', {'form': form})