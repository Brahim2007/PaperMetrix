from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, Mock


class DocumentListTests(TestCase):
    """Tests for the list_documents view."""

    @patch("api.views.requests.get")
    def test_list_documents_with_token(self, mock_get):
        """View should render when a token is present in the session."""
        profile_resp = Mock(ok=True)
        profile_resp.json.return_value = {"display_name": "Tester"}
        docs_resp = Mock(ok=True)
        docs_resp.json.return_value = [{"id": "d1", "title": "Doc"}]
        mock_get.side_effect = [profile_resp, docs_resp]

        session = self.client.session
        session["token"] = {"access_token": "abc"}
        session.save()

        res = self.client.get(reverse("list_documents"))

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "api/library.html")
        self.assertContains(res, "Tester")
        self.assertContains(res, "Doc")
