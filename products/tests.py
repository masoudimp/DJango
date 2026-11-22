from django.test import Client, TestCase
from django.urls import reverse

from .models import Tag


class CreateTagTests(TestCase):
    def test_create_and_show_tag(self):
        response = self.client.post(reverse("products:create_tag"), {"title": "  Cordless  "}, follow=True)
        self.assertEqual(Tag.objects.get().title, "Cordless")
        self.assertContains(response, "Tag added successfully")
        self.assertContains(response, 'value="Cordless"')

    def test_invalid_titles_are_not_saved(self):
        for title in ["", "   ", "x" * 101]:
            with self.subTest(title=title):
                response = self.client.post(reverse("products:create_tag"), {"title": title})
                self.assertEqual(response.status_code, 400)
        self.assertEqual(Tag.objects.count(), 0)

    def test_duplicate_is_rejected(self):
        Tag.objects.create(title="Cordless")
        response = self.client.post(reverse("products:create_tag"), {"title": "Cordless"})
        self.assertContains(response, "already exists", status_code=400)
        self.assertEqual(Tag.objects.count(), 1)

    def test_get_cannot_create_tag(self):
        self.assertEqual(self.client.get(reverse("products:create_tag")).status_code, 405)

    def test_csrf_is_required(self):
        client = Client(enforce_csrf_checks=True)
        url = reverse("products:create_tag")
        self.assertEqual(client.post(url, {"title": "Tools"}).status_code, 403)
        client.get(reverse("products:dashboard"))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(url, {"title": "Tools", "csrfmiddlewaretoken": token}).status_code, 302)
