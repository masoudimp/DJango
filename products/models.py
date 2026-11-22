from django.db import models


class AssetType(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Asset(models.Model):
    title = models.CharField(max_length=200, unique=True)
    url = models.URLField()
    asset_type = models.ForeignKey(
        AssetType,
        on_delete=models.PROTECT,
        related_name="assets",
    )

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title
