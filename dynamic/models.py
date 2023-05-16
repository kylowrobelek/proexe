from django.db import models


class ColumnTypes(models.TextChoices):
    TEXT = "text", "Text"
    BOOL = "bool", "Bool"
    NUMBER = "number", "Number"


class DatabaseTable(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Column(models.Model):
    table = models.ForeignKey(
        DatabaseTable,
        related_name="columns",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    type = models.CharField(
        choices=ColumnTypes.choices, max_length=15, default=ColumnTypes.BOOL
    )

    def __str__(self):
        return f"{self.table} - {self.name}"
