from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DeleteView
from .models import Note
from .forms import NoteForm
from django.urls import reverse_lazy
from .forms import NoteFilterForm


def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('note_list')
    else:
        form = NoteForm()
    return render(request, 'notes/note_form.html', {'form': form})


def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    return render(request, 'notes/note_detail.html', {'note': note})


def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('note_detail', pk=note.pk)
    else:
        form = NoteForm(instance=note)
    return render(request, 'notes/note_form.html', {'form': form})


class NoteDeleteView(DeleteView):
    model = Note
    success_url = reverse_lazy('note_list')
    template_name = 'notes/note_confirm_delete.html'


class NoteListView(ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = NoteFilterForm(self.request.GET)

        if form.is_valid():
            category = form.cleaned_data.get('category')
            reminder_from = form.cleaned_data.get('reminder_from')
            reminder_to = form.cleaned_data.get('reminder_to')
            search = form.cleaned_data.get('search')

            if category:
                queryset = queryset.filter(category=category)

            if reminder_from:
                queryset = queryset.filter(reminder__gte=reminder_from)

            if reminder_to:
                queryset = queryset.filter(reminder__lte=reminder_to)

            if search:
                queryset = queryset.filter(title__icontains=search)

        return queryset.select_related('category').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = NoteFilterForm(self.request.GET)
        return context