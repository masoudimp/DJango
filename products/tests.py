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
        client.get(reverse("products:management"))
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


class EditTagTests(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(title="Cordless")
        self.url = reverse("products:edit_tag", args=[self.tag.pk])

    def test_edit_preserves_id_and_product_links(self):
        category = Category.objects.create(title="Tools")
        product = Product.objects.create(title="Drill", category=category)
        product.tags.add(self.tag)
        response = self.client.post(self.url, {"title": "  Portable  "}, follow=True)
        self.assertRedirects(response, "/manage/?section=tag")
        self.assertContains(response, "Tag updated successfully.")
        self.assertContains(response, 'id="management-success"')
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.title, "Portable")
        self.assertEqual(list(product.tags.all()), [self.tag])
        self.assertEqual(Tag.objects.count(), 1)

    def test_invalid_edit_keeps_record_and_reopens_edit_form(self):
        Tag.objects.create(title="Compact")
        for title in ["", "   ", "x" * 101, "Compact"]:
            with self.subTest(title=title):
                response = self.client.post(self.url, {"title": title})
                self.assertContains(response, 'id="management-tag-invalid"', status_code=400)
                self.assertContains(response, 'data-mode="edit"', status_code=400)
                self.assertContains(response, f'action="{self.url}"', status_code=400)
                self.tag.refresh_from_db()
                self.assertEqual(self.tag.title, "Cordless")

    def test_unchanged_title_is_valid(self):
        self.assertEqual(self.client.post(self.url, {"title": "Cordless"}).status_code, 302)

    def test_method_missing_record_and_csrf(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(self.url, {"title": "Portable"}).status_code, 403)
        client.get(reverse("products:management"))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.url, {
            "title": "Portable", "csrfmiddlewaretoken": token,
        }).status_code, 302)
        self.tag.delete()
        self.assertEqual(self.client.post(self.url, {"title": "Portable"}).status_code, 404)


class CategoryCrudTests(TestCase):
    def setUp(self):
        self.root = Category.objects.create(title="Tools")
        self.child = Category.objects.create(title="Drills", parent=self.root)

    def test_create_list_edit_and_clear_parent(self):
        response = self.client.post(reverse("products:create_category"), {
            "title": "  Cordless  ", "parent": self.child.pk,
        }, follow=True)
        category = Category.objects.get(title="Cordless")
        self.assertEqual(category.parent, self.child)
        self.assertRedirects(response, "/manage/?section=category")
        self.assertContains(response, "Category added successfully.")
        self.assertContains(response, f'data-category="{self.child.pk}"')
        url = reverse("products:edit_category", args=[category.pk])
        response = self.client.post(url, {"title": "Portable", "parent": ""}, follow=True)
        self.assertContains(response, "Category updated successfully.")
        category.refresh_from_db()
        self.assertEqual(category.title, "Portable")
        self.assertIsNone(category.parent)

    def test_invalid_inputs_preserve_form_values_and_database(self):
        url = reverse("products:edit_category", args=[self.child.pk])
        for data in [
            {"title": "Tools", "parent": self.root.pk},
            {"title": "", "parent": self.root.pk},
            {"title": "x" * 101, "parent": self.root.pk},
            {"title": "Changed", "parent": 999999},
        ]:
            with self.subTest(data=data):
                response = self.client.post(url, data)
                self.assertContains(response, 'id="management-category-invalid"', status_code=400)
                self.assertContains(response, f'action="{url}"', status_code=400)
                self.child.refresh_from_db()
                self.assertEqual(self.child.title, "Drills")
                self.assertEqual(self.child.parent, self.root)
        response = self.client.post(reverse("products:create_category"), {"title": "Tools", "parent": self.root.pk})
        self.assertContains(response, 'name="parent"', status_code=400)
        self.assertContains(response, f'value="{self.root.pk}"', status_code=400)
        self.assertEqual(Category.objects.count(), 2)

    def test_rejects_self_and_descendant_parents(self):
        grandchild = Category.objects.create(title="Cordless", parent=self.child)
        url = reverse("products:edit_category", args=[self.root.pk])
        for parent in [self.root, self.child, grandchild]:
            with self.subTest(parent=parent):
                response = self.client.post(url, {"title": "Tools", "parent": parent.pk})
                self.assertContains(response, "cannot be its own parent", status_code=400)
                self.root.refresh_from_db()
                self.assertIsNone(self.root.parent)

    def test_delete_protects_children_and_products(self):
        response = self.client.post(reverse("products:delete_category", args=[self.root.pk]))
        self.assertContains(response, "Move or delete them first", status_code=400)
        product = Product.objects.create(title="Drill", category=self.child)
        response = self.client.post(reverse("products:delete_category", args=[self.child.pk]))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())
        self.assertEqual(Category.objects.count(), 2)
        empty = Category.objects.create(title="Empty")
        response = self.client.post(reverse("products:delete_category", args=[empty.pk]), follow=True)
        self.assertRedirects(response, "/manage/?section=category")
        self.assertContains(response, "Category deleted successfully.")
        self.assertFalse(Category.objects.filter(pk=empty.pk).exists())

    def test_methods_csrf_and_missing_records(self):
        csrf_client = Client(enforce_csrf_checks=True)
        for name in ["create_category", "edit_category", "delete_category"]:
            url = reverse(f"products:{name}", args=[] if name == "create_category" else [self.child.pk])
            self.assertEqual(self.client.get(url).status_code, 405)
            self.assertEqual(csrf_client.post(url, {"title": "Changed"}).status_code, 403)
        for name in ["edit_category", "delete_category"]:
            self.assertEqual(self.client.post(reverse(f"products:{name}", args=[999999])).status_code, 404)
