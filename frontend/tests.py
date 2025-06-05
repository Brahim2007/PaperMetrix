from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from api.models import Article, Authors, Tag, Library
from frontend.services import recommendation_service
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


class ReccomTests(TestCase):
    def setUp(self):
        self.author = Authors.objects.create(name='Auth', done=True)
        with patch('api.models.requests.get') as mock_get:
            mock_get.return_value.ok = False
            self.art1 = Article.objects.create(
                title='Dogs rule',
                type='journal',
                year=2020,
                source='src',
                publisher='pub',
                id='d1',
                link='http://example.com',
                abstract='All about dogs',
                identifiers={'doi': '10.1/d1'},
            )
        self.art1.authors.add(self.author)
        with patch('api.models.requests.get') as mock_get:
            mock_get.return_value.ok = False
            self.art2 = Article.objects.create(
                title='Cats world',
                type='journal',
                year=2020,
                source='src',
                publisher='pub',
                id='c1',
                link='http://example.com',
                abstract='Cats are great',
                identifiers={'doi': '10.1/c1'},
            )
        self.art2.authors.add(self.author)

    def tearDown(self):
        import os
        from django.conf import settings
        for f in ['tfidf.pickle', 'tfidf_fit.pickle']:
            path = os.path.join(settings.BASE_DIR, f)
            if os.path.exists(path):
                os.remove(path)

    def test_similar_items(self):
        from frontend import reccom
        reccom.rebuild_tfidf_matrix()
        sims = reccom.get_similar_items('cats', 0, 1)
        self.assertEqual(sims[0], 'c1')


class RecommendWithFallbackTests(TestCase):
    """Tests for the recommend_with_fallback helper."""

    def test_returns_deepseek_results_when_available(self):
        ids = ['x1', 'x2']
        with patch('api.deepseek_client.recommend_articles', return_value=ids) as deep_mock, \
             patch('frontend.services.recommendation_service.deepseek', new=deep_mock), \
             patch('frontend.services.recommendation_service.get_similar_items') as sim_mock:
            result = recommendation_service.recommend_with_fallback('prompt', limit=2)
        self.assertEqual(result, ids)
        deep_mock.assert_called_once_with('prompt', limit=2)
        sim_mock.assert_not_called()

    def test_falls_back_when_deepseek_empty(self):
        fallback = ['f1', 'f2']
        with patch('api.deepseek_client.recommend_articles', return_value=[]) as deep_mock, \
             patch('frontend.services.recommendation_service.deepseek', new=deep_mock), \
             patch('frontend.services.recommendation_service.get_similar_items', return_value=fallback) as sim_mock:
            result = recommendation_service.recommend_with_fallback('prompt', limit=2)
        self.assertEqual(result, fallback)
        deep_mock.assert_called_once_with('prompt', limit=2)
        sim_mock.assert_called_once_with('prompt', 1, 2)

