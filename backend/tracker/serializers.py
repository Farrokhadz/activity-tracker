from rest_framework import serializers
from .models import Category, Entry


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_default']

    def validate_name(self, value):
        # Category names are unique ignoring case ("Gym" and "gym" are the same category).
        # The database enforces this too, but checking here gives a clean 400 instead of a 500.
        duplicates = Category.objects.filter(name__iexact=value)
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError('A category with this name already exists.')
        return value


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ['id', 'date', 'category', 'duration', 'note']
