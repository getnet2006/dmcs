from rest_framework import serializers
from .models import Document, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    

    class Meta:
        model = Document
        fields = '__all__'