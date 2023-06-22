from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='New title',
        text='New text',
    )
    return news


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News.objects.create(title=f'Новость {i}',
                            text='Просто текст.',
                            date=today - timedelta(days=i))
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return all_news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='New comment text',
    )
    return comment


@pytest.fixture
def comments(author, news):
    comments = []
    for i in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Text {i}'
        )
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def pk_for_args_news(news):
    return news.pk,


@pytest.fixture
def pk_for_args_comment(comment):
    return comment.pk,


@pytest.fixture
def form_data():
    return {
        'text': 'New form comment text'
    }
