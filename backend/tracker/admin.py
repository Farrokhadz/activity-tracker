from django.contrib import admin
from .models import Category, Entry


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default')


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'duration')
    list_filter = ('category',)
