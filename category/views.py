from .models import Category
from .serializers import CategorySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response

# Create your views here.


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_user_object(self, queryset=None):
        obj = self.request.user
        return obj

    def create(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'product category saved successfully', "status": status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, exception=True)

    def update(self, request, *args, **kwargs):
        category = self.queryset.get(pk=kwargs.get('id'))
        
        serializer = self.serializer_class(
            category, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({'msg': 'product category updated successfully', "status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, exception=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance)

        return Response({'msg': 'product category fetched successfully', "status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        
        instance.delete()
        
        return Response({'msg': 'product category deleted successfully', "status": status.HTTP_204_NO_CONTENT}, status=status.HTTP_204_NO_CONTENT)
