from django.test import Client, TestCase
from django.urls import reverse

from .models import Category, Product, Tag


class CreateTagTests(TestCase):
    def test_management_create_returns_to_tags_with_success_modal(self):
        response = self.client.post(reverse("products:create_tag"), {
            "title": "Compact", "source": "management",
        }, follow=True)
        self.assertRedirects(response, "/manage/?section=tag")
        self.assertEqual(Tag.objects.get().title, "Compact")
        self.assertContains(response, 'id="management-success"')
        self.assertContains(response, "Tag added successfully")

    def test_management_duplicate_reopens_form_with_error(self):
        Tag.objects.create(title="Compact")
        response = self.client.post(reverse("products:create_tag"), {
            "title": "Compact", "source": "management",
        })
        self.assertContains(response, 'id="management-tag-invalid"', status_code=400)
        self.assertContains(response, 'value="Compact"', status_code=400)
        self.assertContains(response, "already exists", status_code=400)
        self.assertEqual(Tag.objects.count(), 1)

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


class DeleteTagTests(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(title="Cordless")
        self.url = reverse("products:delete_tag", args=[self.tag.pk])

    def test_delete_removes_tag_but_keeps_product_and_other_tags(self):
        category = Category.objects.create(title="Tools")
        product = Product.objects.create(title="Drill", category=category)
        other_tag = Tag.objects.create(title="Compact")
        product.tags.add(self.tag, other_tag)
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, "Tag deleted successfully.")
        self.assertFalse(Tag.objects.filter(pk=self.tag.pk).exists())
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())
        self.assertEqual(list(product.tags.all()), [other_tag])

    def test_get_does_not_delete(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertTrue(Tag.objects.filter(pk=self.tag.pk).exists())

    def test_missing_tag_returns_404(self):
        self.tag.delete()
        self.assertEqual(self.client.post(self.url).status_code, 404)

    def test_delete_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(self.url).status_code, 403)
        self.assertTrue(Tag.objects.filter(pk=self.tag.pk).exists())
        client.get(reverse("products:management"))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.url, {"csrfmiddlewaretoken": token}).status_code, 302)
        self.assertFalse(Tag.objects.filter(pk=self.tag.pk).exists())
