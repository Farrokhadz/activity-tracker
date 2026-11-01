from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Entry
from .serializers import CategorySerializer, EntrySerializer


class CategoryListCreateView(APIView):
    def get(self, request):
        categories = Category.objects.order_by('name')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EntryListCreateView(APIView):
    def get(self, request):
        entries = Entry.objects.all()

        # Optional filters: ?date=YYYY-MM-DD, ?from=YYYY-MM-DD, ?to=YYYY-MM-DD, ?category=<id>
        for param, lookup in (('date', 'date'), ('from', 'date__gte'), ('to', 'date__lte')):
            value = request.query_params.get(param)
            if value is None:
                continue
            try:
                parsed = parse_date(value)
            except ValueError:
                parsed = None
            if parsed is None:
                return Response(
                    {param: ['Enter a valid date in YYYY-MM-DD format.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            entries = entries.filter(**{lookup: parsed})

        category = request.query_params.get('category')
        if category is not None:
            if not category.isdigit():
                return Response(
                    {'category': ['Enter a valid category id.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            entries = entries.filter(category_id=int(category))

        serializer = EntrySerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
