from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from api.models import Article, Authors, Tag, Library
import numpy as np

class TagViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email='user@example.com',
            password='pass',
            full_name='User',
            user_roles='other'
        )
        self.client.login(email='user@example.com', password='pass')
        self.author = Authors.objects.create(name='Auth', done=True)
        with patch('api.models.requests.get') as mock_get:
            mock_get.return_value.ok = False
            self.article = Article.objects.create(
                title='Title',
                type='journal',
                year=2020,
                source='src',
                publisher='pub',
                id='a1',
                link='http://example.com',
                abstract='abs',
                identifiers={'doi': '10.1/abc'},
            )
        self.article.authors.add(self.author)

    def test_add_and_remove_tag(self):
        res = self.client.post(reverse('add_tag', args=[self.article.pk]), {'tag': 'tag1'})
        self.assertEqual(res.status_code, 200)
        tag = Tag.objects.get(tag='tag1')
        self.assertIn(self.article, tag.article.all())

        res = self.client.post(reverse('remove_tag', args=[tag.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Tag.objects.filter(pk=tag.pk).exists())

    def test_remove_missing_tag(self):
        res = self.client.post(reverse('remove_tag', args=[999]))
        self.assertEqual(res.status_code, 200)

    @patch('frontend.views.get_similar_items')
    def test_library_recommendation(self, mock_similar):
        mock_similar.return_value = np.array([[self.article.pk, 1.0]])
        library = Library.objects.create(name='lib', user=self.user)
        library.articles.add(self.article)
        res = self.client.get(reverse('get_library_recommendation', args=[library.pk]))
        self.assertEqual(res.status_code, 200)

