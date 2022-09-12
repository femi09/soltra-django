from rest_framework import serializers
from .models import Product
from authentication.serializers import UserSerializer
from category.serializers import CategorySerializer


class ProductSerializer(serializers.ModelSerializer):
    # qs = Product.objects.prefetch_related('user', 'category')
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = "__all__"
        
    
    