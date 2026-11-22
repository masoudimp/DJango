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
        self.assertContains(response, 'data-label="Cordless"')

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


class ProductCrudTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Equipment")
        self.tag = Tag.objects.create(title='Portable | "Small"')
        self.other_tag = Tag.objects.create(title="Heavy")

    def test_create_and_render_in_dashboard_and_management(self):
        response = self.client.post(reverse("products:create_product"), {
            "title": "  Test drill  ", "category": self.category.pk,
            "description": "First line\nSecond line", "tags": [self.tag.pk, self.other_tag.pk],
        }, follow=True)
        product = Product.objects.get()
        self.assertEqual(product.title, "Test drill")
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.description, "First line\nSecond line")
        self.assertCountEqual(product.tags.all(), [self.tag, self.other_tag])
        self.assertIsNone(product.image)
        self.assertRedirects(response, "/manage/?section=product")
        self.assertContains(response, "Product added successfully.")
        self.assertContains(response, f'data-edit-url="{reverse("products:edit_product", args=[product.pk])}"')
        self.assertContains(response, f'data-category="{self.category.pk}"')
        response = self.client.get(reverse("products:dashboard"))
        self.assertContains(response, "Test drill")
        self.assertContains(response, "Equipment")
        self.assertContains(response, "Portable | &quot;Small&quot;")
        self.assertContains(response, "First line\nSecond line")

    def test_edit_replaces_tags_and_can_clear_optional_fields(self):
        product = Product.objects.create(title="Before", category=self.category, description="Old")
        product.tags.add(self.tag)
        category = Category.objects.create(title="Other")
        url = reverse("products:edit_product", args=[product.pk])
        response = self.client.post(url, {
            "title": "After", "category": category.pk, "tags": [self.other_tag.pk], "description": "Updated",
        }, follow=True)
        self.assertContains(response, "Product updated successfully.")
        product.refresh_from_db()
        self.assertEqual(product.title, "After")
        self.assertEqual(product.category, category)
        self.assertEqual(product.description, "Updated")
        self.assertEqual(list(product.tags.all()), [self.other_tag])
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.client.post(url, {"title": "After", "category": category.pk}).status_code, 302)
        product.refresh_from_db()
        self.assertFalse(product.description)
        self.assertFalse(product.tags.exists())

    def test_invalid_create_does_not_save(self):
        for data in [
            {"title": "", "category": self.category.pk},
            {"title": " " * 5, "category": self.category.pk},
            {"title": "x" * 201, "category": self.category.pk},
            {"title": "Missing category"},
            {"title": "Invalid category", "category": 999999},
            {"title": "Invalid tag", "category": self.category.pk, "tags": [999999]},
        ]:
            with self.subTest(data=data):
                response = self.client.post(reverse("products:create_product"), data)
                self.assertContains(response, 'id="management-product-invalid"', status_code=400)
                self.assertFalse(Product.objects.exists())

    def test_invalid_edit_preserves_database_and_submitted_values(self):
        from html.parser import HTMLParser

        class Inputs(HTMLParser):
            def __init__(self, html):
                super().__init__()
                self.inputs = []
                self.feed(html)

            def handle_starttag(self, tag, attrs):
                if tag == "input":
                    self.inputs.append(dict(attrs))

        product = Product.objects.create(title="Original", category=self.category, description="Original text")
        product.tags.add(self.tag)
        url = reverse("products:edit_product", args=[product.pk])
        response = self.client.post(url, {
            "title": "", "category": self.category.pk,
            "description": 'Submitted <text> & "quotes"', "tags": [self.other_tag.pk],
        })
        self.assertContains(response, f'action="{url}"', status_code=400)
        self.assertContains(response, 'id="management-product-invalid"', status_code=400)
        self.assertContains(response, "Submitted &lt;text&gt; &amp; &quot;quotes&quot;", status_code=400)
        inputs = Inputs(response.content.decode()).inputs
        checked = [item["value"] for item in inputs if item.get("name") == "tags" and "checked" in item]
        self.assertEqual(checked, [str(self.other_tag.pk)])
        category = next(item for item in inputs if item.get("id") == "new-product-category-value")
        self.assertEqual(category["value"], str(self.category.pk))
        product.refresh_from_db()
        self.assertEqual(product.title, "Original")
        self.assertEqual(product.description, "Original text")
        self.assertEqual(list(product.tags.all()), [self.tag])

    def test_delete_keeps_category_tags_and_other_products(self):
        product = Product.objects.create(title="Delete me", category=self.category)
        other = Product.objects.create(title="Keep me", category=self.category)
        product.tags.add(self.tag)
        other.tags.add(self.tag)
        response = self.client.post(reverse("products:delete_product", args=[product.pk]), follow=True)
        self.assertRedirects(response, "/manage/?section=product")
        self.assertContains(response, "Product deleted successfully.")
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
        self.assertTrue(Tag.objects.filter(pk=self.tag.pk).exists())
        self.assertEqual(list(other.tags.all()), [self.tag])

    def test_methods_missing_records_and_csrf(self):
        product = Product.objects.create(title="Original", category=self.category)
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("products:management"))
        token = client.cookies["csrftoken"].value
        for name in ["create_product", "edit_product", "delete_product"]:
            url = reverse(f"products:{name}", args=[] if name == "create_product" else [product.pk])
            self.assertEqual(self.client.get(url).status_code, 405)
            data = {"title": "Changed", "category": self.category.pk}
            self.assertEqual(client.post(url, data).status_code, 403)
            self.assertEqual(client.post(url, {**data, "csrfmiddlewaretoken": token}).status_code, 302)
        for name in ["edit_product", "delete_product"]:
            self.assertEqual(self.client.post(reverse(f"products:{name}", args=[999999])).status_code, 404)

    def test_empty_dashboard_and_optional_fields(self):
        response = self.client.get(reverse("products:dashboard"))
        self.assertContains(response, "No products found.")
        response = self.client.post(reverse("products:create_product"), {
            "title": "Minimal", "category": self.category.pk,
        })
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get()
        self.assertFalse(product.tags.exists())
        self.assertFalse(product.description)
        response = self.client.get(reverse("products:dashboard"))
        self.assertContains(response, "No description available.")
        self.assertContains(response, "image-not-available.jpg")


class ProductFilterTests(TestCase):
    def setUp(self):
        self.parent = Category.objects.create(title="Electrical")
        self.child = Category.objects.create(title="Breakers", parent=self.parent)
        self.leaf = Category.objects.create(title="MCB", parent=self.child)
        self.other = Category.objects.create(title="Lighting")
        self.red = Tag.objects.create(title="Red")
        self.blue = Tag.objects.create(title="Blue")
        self.first = Product.objects.create(title="Circuit Breaker", category=self.leaf, description="Indoor protection")
        self.first.tags.add(self.red, self.blue)
        self.second = Product.objects.create(title="Lamp", category=self.other, description="INDOOR lighting")
        self.second.tags.add(self.blue)
        self.third = Product.objects.create(title="Panel", category=self.parent)
        self.url = reverse("products:product_list")

    def assert_products(self, params, expected):
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(list(response.context["products"]), expected)
        return response

    def test_empty_and_blank_filters_return_all(self):
        expected = [self.first, self.second, self.third]
        self.assert_products({}, expected)
        self.assert_products({"categoryId": "", "tagIds": [""], "search": "   "}, expected)

    def test_category_includes_descendants_and_unknown_returns_empty(self):
        self.assert_products({"categoryId": self.parent.pk}, [self.first, self.third])
        self.assert_products({"categoryId": self.child.pk}, [self.first])
        self.assert_products({"categoryId": self.leaf.pk}, [self.first])
        self.assert_products({"categoryId": 999999}, [])

    def test_any_selected_tag_matches_without_duplicates(self):
        self.assert_products({"tagIds": [self.red.pk]}, [self.first])
        response = self.assert_products({"tagIds": [self.red.pk, self.blue.pk, self.red.pk]}, [self.first, self.second])
        self.assertContains(response, 'aria-label="View details for Circuit Breaker"', count=1)
        self.assert_products({"tagIds": [999999]}, [])

    def test_search_contains_title_or_description_case_insensitively(self):
        self.assert_products({"search": "  cUiT  "}, [self.first])
        self.assert_products({"search": "indoor"}, [self.first, self.second])
        self.assert_products({"search": "missing"}, [])
        self.assert_products({"search": "%"}, [])

    def test_filters_combine_with_and(self):
        self.assert_products({"categoryId": self.parent.pk, "tagIds": [self.blue.pk], "search": "indoor"}, [self.first])
        self.assert_products({"categoryId": self.other.pk, "tagIds": [self.red.pk]}, [])

    def test_malformed_ids_return_400(self):
        for key in ["categoryId", "tagIds"]:
            for value in ["abc", "1.5", "-1", "0", "9223372036854775808"]:
                with self.subTest(key=key, value=value):
                    self.assertEqual(self.client.get(self.url, {key: value}).status_code, 400)
        self.assertEqual(self.client.post(self.url).status_code, 405)

    def test_dto_normalizes_types_and_empty_values(self):
        from django.http import QueryDict
        from .dtos import ProductFilterRequest
        self.assertEqual(ProductFilterRequest.from_query(QueryDict("")), ProductFilterRequest())
        dto = ProductFilterRequest.from_query(QueryDict("categoryId=2&tagIds=3&tagIds=4&tagIds=3&search=++lamp++"))
        self.assertEqual(dto, ProductFilterRequest(categoryId=2, tagIds=[3, 4], search="lamp"))

    def test_fragment_uses_constant_number_of_queries(self):
        with self.assertNumQueries(2):
            response = self.client.get(self.url)
        self.assertNotContains(response, "<html")
        self.assertContains(response, "Circuit Breaker")
        self.assertContains(response, "Red")
