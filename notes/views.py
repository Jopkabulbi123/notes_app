from django.shortcuts import render
from datetime import datetime

def note_list(request):
    test_notes = [
        {'title': 'Перша нотатка', 'content': 'Привіт від Django!', 'created_at': datetime.now()},
        {'title': 'Список покупок', 'content': 'Хліб, молоко, яйця', 'created_at': datetime.now()}
    ]
    return render(request, 'notes/index.html', {'notes': test_notes})