from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note_author = Note.objects.create(
            title='Название заметки 1',
            text='Текстовый текст 1',
            slug='text1',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        params = (
            (self.author, True),
            (self.reader, False),
        )
        for name, note_in_list in params:
            url = reverse('notes:list')
            self.client.force_login(name)
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertEqual(self.note_author in object_list, note_in_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note_author.slug,))
        )
        self.client.force_login(self.author)
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
