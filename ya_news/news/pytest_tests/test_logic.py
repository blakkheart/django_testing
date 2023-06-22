from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cannot_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.pk, ))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news, form_data):
    url = reverse('news:detail', args=(news.pk, ))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cannot_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Some text, {BAD_WORDS[0]}, text again'}
    url = reverse('news:detail', args=(news.pk, ))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING,
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, news, comment):
    url_comment = reverse('news:delete', args=(comment.pk, ))
    url_news = reverse('news:detail', args=(news.pk, ))
    response = author_client.delete(url_comment)
    assertRedirects(response, f'{url_news}#comments')
    comment_count = Comment.objects.count()
    assert comment_count == 0


def test_user_cannot_delete_comment_of_another_user(admin_client, comment):
    url_comment = reverse('news:delete', args=(comment.pk, ))
    response = admin_client.delete(url_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, news, comment, form_data):
    url_comment = reverse('news:edit', args=(comment.pk, ))
    url_news = reverse('news:detail', args=(news.pk, ))
    response = author_client.post(url_comment, data=form_data)
    assertRedirects(response, f'{url_news}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cannot_edit_comment_of_another_user(
        admin_client, comment, form_data):
    comment_text = comment.text
    url_comment = reverse('news:edit', args=(comment.pk, ))
    response = admin_client.post(url_comment, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
