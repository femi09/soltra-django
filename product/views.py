from unicodedata import category
from django.shortcuts import render
from rest_framework import views, status, generics
from rest_framework.filters import SearchFilter, BaseFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer
from django_filters import rest_framework as filters
from django.db.models import F, Count, Q
from rest_framework.pagination import PageNumberPagination

# Create your views here.


class BasePagination(PageNumberPagination):
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        return Response({
            'msg': "products fetched successfully",
            "status": status.HTTP_200_OK,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "limit": self.get_page_size(self.request),
            'count': self.page.paginator.count,
            'results': data
        })


class IsUserFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__name')

    class Meta:
        model = Product
        fields = ['category', 'brand']


class ProductViewSet(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ProductFilter
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    search_fields = ['name', 'description', 'brand', 'category__name']
    pagination_class = BasePagination

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        return queryset

    def get_user_object(self, queryset=None):
        obj = self.request.user
        return obj

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = ProductSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response({'msg': "products fetched successfully!", "status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        category_id = request.data['category']

        if serializer.is_valid():
            serializer.save(user=self.get_user_object(),
                            category_id=category_id)
            return Response({'msg': "product created successfully!", "status": status.HTTP_201_CREATED, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, exception=True)


class ProductByUserView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ProductFilter
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter, IsUserFilterBackend)
    search_fields = ['name', 'description', 'brand', 'category__name']
    pagination_class = BasePagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = ProductSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response({'msg': "products fetched successfully!", "status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)

class ProductUpdateDeleteViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_user_object(self, queryset=None):
        obj = self.request.user
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = ProductSerializer(instance=instance)

        return Response({'msg': "product fetched successfully!", "status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.user != self.get_user_object():
            return Response({'msg': 'not authorized to update this product', 'status': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST, exception=True)

        serializer = ProductSerializer(instance=instance, data=request.data)

        if serializer.is_valid():
            serializer.save(user=self.get_user_object())

            return Response({'msg': "product updated successfully!", "status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, exception=True)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.user != self.get_user_object():
            return Response({'msg': 'not authorized to delete this product', 'status': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST, exception=True)

        instance.delete()

        return Response({'msg': 'product deleted successfully', "status": status.HTTP_204_NO_CONTENT}, status=status.HTTP_204_NO_CONTENT)
