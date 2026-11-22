from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Tag


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


class DjangoAdminTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        # Test database only; no real administrator credentials are created.
        self.user = get_user_model().objects.create(username="admin-test", is_staff=True, is_superuser=True)
        self.client.force_login(self.user)

    def test_registered_models_and_add_pages(self):
        for model in ["product", "category", "tag"]:
            self.assertEqual(self.client.get(reverse(f"admin:products_{model}_changelist")).status_code, 200)
            self.assertEqual(self.client.get(reverse(f"admin:products_{model}_add")).status_code, 200)
        response = self.client.get(reverse("admin:products_product_add"))
        self.assertNotContains(response, 'name="image"')

    def test_admin_can_create_and_edit_product_with_relationships(self):
        self.client.post(reverse("admin:products_category_add"), {"title": "Tools", "parent": "", "_save": "Save"})
        self.client.post(reverse("admin:products_tag_add"), {"title": "Portable", "_save": "Save"})
        category = Category.objects.get(title="Tools")
        tag = Tag.objects.get(title="Portable")
        response = self.client.post(reverse("admin:products_product_add"), {
            "title": "Drill", "description": "For installation work", "category": category.pk,
            "tags": [tag.pk], "_save": "Save",
        })
        self.assertRedirects(response, reverse("admin:products_product_changelist"))
        product = Product.objects.get(title="Drill")
        self.assertEqual(product.category, category)
        self.assertEqual(list(product.tags.all()), [tag])
        self.assertEqual(product.description, "For installation work")
        response = self.client.post(reverse("admin:products_product_change", args=[product.pk]), {
            "title": "Updated drill", "description": "", "category": category.pk, "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        product.refresh_from_db()
        self.assertEqual(product.title, "Updated drill")
        self.assertFalse(product.tags.exists())

    def test_admin_category_form_rejects_cycles(self):
        root = Category.objects.create(title="Root")
        child = Category.objects.create(title="Child", parent=root)
        for parent in [root, child]:
            response = self.client.post(reverse("admin:products_category_change", args=[root.pk]), {
                "title": "Root", "parent": parent.pk, "_save": "Save",
            })
            self.assertContains(response, "cannot be its own parent")
            root.refresh_from_db()
            self.assertIsNone(root.parent)

    def test_admin_requires_staff_login(self):
        from django.contrib.auth import get_user_model
        self.client.logout()
        url = reverse("admin:products_product_changelist")
        self.assertRedirects(self.client.get(url), f'{reverse("admin:login")}?next={url}')
        user = get_user_model().objects.create(username="non-staff")
        self.client.force_login(user)
        self.assertRedirects(self.client.get(url), f'{reverse("admin:login")}?next={url}')

    def test_admin_delete_keeps_shared_category_and_tag(self):
        category = Category.objects.create(title="Tools")
        tag = Tag.objects.create(title="Portable")
        product = Product.objects.create(title="Drill", category=category)
        product.tags.add(tag)
        response = self.client.post(reverse("admin:products_product_delete", args=[product.pk]), {"post": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())
        self.assertTrue(Tag.objects.filter(pk=tag.pk).exists())

    def test_admin_cannot_delete_category_with_products(self):
        category = Category.objects.create(title="Tools")
        Product.objects.create(title="Drill", category=category)
        response = self.client.post(reverse("admin:products_category_delete", args=[category.pk]), {"post": "yes"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())


class DashboardNavigationTests(TestCase):
    def test_header_links_to_django_admin(self):
        response = self.client.get(reverse("products:dashboard"))
        self.assertContains(response, f'href="{reverse("admin:index")}"')
        self.assertNotContains(response, "/manage/")
        self.assertNotContains(response, 'id="admin-modal"')

    def test_custom_management_routes_are_removed(self):
        for url in ["/manage/", "/tags/create/", "/tags/1/edit/", "/tags/1/delete/",
                    "/categories/create/", "/categories/1/edit/", "/categories/1/delete/",
                    "/products/create/", "/products/1/edit/", "/products/1/delete/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url).status_code, 404)
