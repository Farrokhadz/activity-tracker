from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Entry(models.Model):
    date = models.DateField()
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='entries',
    )
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category.name} - {self.duration}min on {self.date}"
