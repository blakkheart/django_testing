
from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestCreateNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.form_data = {
            'title': 'Новое название',
            'text': 'Новый текст',
            'slug': 'new_slug',
        }

    def test_user_can_crate_note(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        params = (
            (new_note.title, self.form_data['title']),
            (new_note.text, self.form_data['text']),
            (new_note.slug, self.form_data['slug']),
            (new_note.author, self.author)
        )
        for result, expected_result in params:
            with self.subTest(name=result):
                self.assertEqual(result, expected_result)

    def test_anon_user_cannot_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestEditDeleteNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Название заметки 1',
            text='Текстовый текст 1',
            slug='text1',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новое название',
            'text': 'Новый текст',
            'slug': 'new_slug',
        }

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        params = (
            (self.note.title, self.form_data['title']),
            (self.note.text, self.form_data['text']),
            (self.note.slug, self.form_data['slug'])
        )
        for result, expected_result in params:
            with self.subTest(name=result):
                self.assertEqual(result, expected_result)

    def test_other_user_cannot_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.reader)
        response = self.client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.pk)
        params = (
            (self.note.title, note_from_db.title),
            (self.note.text, note_from_db.text),
            (self.note.slug, note_from_db.slug)
        )
        for result, expected_result in params:
            with self.subTest(name=result):
                self.assertEqual(result, expected_result)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.reader)
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
