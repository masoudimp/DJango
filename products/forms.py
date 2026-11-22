from django import forms

from .models import Category, Tag


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["title"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["title", "parent"]

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        # Walk upwards to reject both self-parenting and descendant parents.
        ancestor = parent
        visited = set()
        while ancestor is not None:
            if ancestor.pk == self.instance.pk or ancestor.pk in visited:
                raise forms.ValidationError("A category cannot be its own parent or a descendant's child.")
            visited.add(ancestor.pk)
            ancestor = ancestor.parent
        return parent
