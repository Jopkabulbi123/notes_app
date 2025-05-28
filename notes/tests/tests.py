import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from notes.models import Note, Category
from notes.forms import NoteForm
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def category(user):
    return Category.objects.create(title="Test Category", user=user)


@pytest.fixture
def note(category, user):
    return Note.objects.create(
        title="Test Note",
        text="Test text",
        category=category,
        user=user
    )

@pytest.mark.django_db
def test_note_creation(category, user):
    note = Note.objects.create(
        title="Test Note",
        text="Test text",
        category=category,
        user=user
    )
    assert note.id is not None
    assert str(note) == "Test Note"
    assert note.category == category
    assert note.created_at is not None


@pytest.mark.django_db
def test_note_with_reminder(category, user):
    future_time = timezone.now() + timedelta(days=1)
    note = Note.objects.create(
        title="Note with reminder",
        text="Test reminder",
        category=category,
        reminder=future_time,
        user=user
    )
    assert note.reminder == future_time


@pytest.mark.django_db
def test_note_form_valid(category):
    form_data = {
        'title': 'Form Test',
        'text': 'Form text',
        'category': category.id
    }
    form = NoteForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_note_form_missing_title(category):
    form_data = {
        'text': 'Form text',
        'category': category.id
    }
    form = NoteForm(data=form_data)
    assert not form.is_valid()
    assert 'title' in form.errors

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_note_create_view(client, category, user):
    await sync_to_async(client.force_login)(user)
    url = reverse('note_create')

    response = await sync_to_async(client.get)(url)
    assert response.status_code == 200

    response = await sync_to_async(client.post)(url, {
        'title': 'View Test',
        'text': 'View text',
        'category': category.id
    })
    assert response.status_code == 302
    assert await sync_to_async(Note.objects.filter)(title='View Test').exists()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_note_detail_view(client, note, user):
    await sync_to_async(client.force_login)(user)
    url = reverse('note_detail', kwargs={'pk': note.pk})
    response = await sync_to_async(client.get)(url)
    assert response.status_code == 200
    assert note.title.encode() in response.content


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_note_edit_view(client, note, category, user):
    await sync_to_async(client.force_login)(user)
    url = reverse('note_edit', kwargs={'pk': note.pk})

    response = await sync_to_async(client.get)(url)
    assert response.status_code == 200

    new_title = "Updated Title"
    response = await sync_to_async(client.post)(url, {
        'title': new_title,
        'text': note.text,
        'category': category.id
    })
    assert response.status_code == 302
    await sync_to_async(note.refresh_from_db)()
    assert note.title == new_title


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_note_delete_view(client, note, user):
    await sync_to_async(client.force_login)(user)
    url = reverse('note_delete', kwargs={'pk': note.pk})

    # Test GET request
    response = await sync_to_async(client.get)(url)
    assert response.status_code == 200

    # Test POST request
    response = await sync_to_async(client.post)(url)
    assert response.status_code == 302
    assert not await sync_to_async(Note.objects.filter)(pk=note.pk).exists()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_note_list_view(client, note, user):
    await sync_to_async(client.force_login)(user)
    url = reverse('note_list')
    response = await sync_to_async(client.get)(url)
    assert response.status_code == 200
    assert note.title.encode() in response.content


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_note_list_filtering(client, category, user):
    await sync_to_async(client.force_login)(user)

    # Create test notes
    await sync_to_async(Note.objects.create)(
        title="Work Note",
        text="Content",
        category=category,
        user=user
    )
    await sync_to_async(Note.objects.create)(
        title="Personal Note",
        text="Content",
        user=user
    )

    url = reverse('note_list') + f'?category={category.id}'
    response = await sync_to_async(client.get)(url)
    assert response.status_code == 200
    assert b"Work Note" in response.content
    assert b"Personal Note" not in response.content

    url = reverse('note_list') + '?search=Personal'
    response = await sync_to_async(client.get)(url)
    assert b"Work Note" not in response.content
    assert b"Personal Note" in response.content