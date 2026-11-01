from django.urls import path
from .views import CategoryListCreateView, EntryListCreateView

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('entries/', EntryListCreateView.as_view(), name='entry-list-create'),
]
