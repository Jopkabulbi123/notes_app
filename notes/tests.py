import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from notes.models import Note, Category
from notes.forms import NoteForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def category():
    return Category.objects.create(name="Test Category")

@pytest.fixture
def note(category):
    return Note.objects.create(
        title="Test Note",
        content="Test content",
        category=category
    )



@pytest.mark.django_db
def test_note_creation(category):
    note = Note.objects.create(
        title="Test Note",
        content="Test content",
        category=category
    )
    assert note.id is not None
    assert str(note) == "Test Note"
    assert note.category == category
    assert note.created_at is not None


@pytest.mark.django_db
def test_note_with_reminder(category):
    future_time = timezone.now() + timedelta(days=1)
    note = Note.objects.create(
        title="Note with reminder",
        content="Test reminder",
        category=category,
        reminder=future_time
    )
    assert note.reminder == future_time


@pytest.mark.django_db
def test_note_form_valid(category):
    form_data = {
        'title': 'Form Test',
        'content': 'Form content',
        'category': category.id
    }
    form = NoteForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_note_form_missing_title(category):
    form_data = {
        'content': 'Form content',
        'category': category.id
    }
    form = NoteForm(data=form_data)
    assert not form.is_valid()
    assert 'title' in form.errors


@pytest.mark.django_db
def test_note_create_view(client, category):
    url = reverse('note_create')
    response = client.get(url)
    assert response.status_code == 200

    response = client.post(url, {
        'title': 'View Test',
        'content': 'View content',
        'category': category.id
    })
    assert response.status_code == 302
    assert Note.objects.filter(title='View Test').exists()


@pytest.mark.django_db
def test_note_detail_view(client, note):
    url = reverse('note_detail', kwargs={'pk': note.pk})
    response = client.get(url)
    assert response.status_code == 200
    assert note.title.encode() in response.content


@pytest.mark.django_db
def test_note_edit_view(client, note, category):
    url = reverse('note_edit', kwargs={'pk': note.pk})
    response = client.get(url)
    assert response.status_code == 200

    new_title = "Updated Title"
    response = client.post(url, {
        'title': new_title,
        'content': note.content,
        'category': category.id
    })
    assert response.status_code == 302
    note.refresh_from_db()
    assert note.title == new_title


@pytest.mark.django_db
def test_note_delete_view(client, note):
    url = reverse('note_delete', kwargs={'pk': note.pk})
    response = client.get(url)
    assert response.status_code == 200

    response = client.post(url)
    assert response.status_code == 302
    assert not Note.objects.filter(pk=note.pk).exists()


@pytest.mark.django_db
def test_note_list_view(client, note):
    url = reverse('note_list')
    response = client.get(url)
    assert response.status_code == 200
    assert note.title.encode() in response.content


@pytest.mark.django_db
def test_note_list_filtering(client, category):
    Note.objects.create(title="Work Note", content="Content", category=category)
    Note.objects.create(title="Personal Note", content="Content")

    # Filter by category
    url = reverse('note_list') + f'?category={category.id}'
    response = client.get(url)
    assert response.status_code == 200
    assert b"Work Note" in response.content
    assert b"Personal Note" not in response.content

    # Search filter
    url = reverse('note_list') + '?search=Personal'
    response = client.get(url)
    assert b"Work Note" not in response.content
    assert b"Personal Note" in response.content