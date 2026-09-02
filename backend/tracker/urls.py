from django.urls import path
from .views import EntryListCreateView

urlpatterns = [
    path('entries/', EntryListCreateView.as_view(), name='entry-list-create'),
]
