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
        serializer = EntrySerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
