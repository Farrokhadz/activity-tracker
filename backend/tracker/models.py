from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Lower


class Category(models.Model):
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_category_name_case_insensitive',
                violation_error_message='A category with this name already exists.',
            ),
        ]

    def __str__(self):
        return self.name


class Entry(models.Model):
    date = models.DateField()
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='entries',
    )
    duration = models.PositiveIntegerField(
        help_text="Duration in minutes",
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
    )
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.category.name} - {self.duration}min on {self.date}"
