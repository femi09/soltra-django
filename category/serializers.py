from pyexpat import model
from rest_framework import serializers
from .models import Category
from rest_framework.validators import UniqueValidator

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Category.objects.all())])
    class Meta:
        model = Category
        fields = '__all__'
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance