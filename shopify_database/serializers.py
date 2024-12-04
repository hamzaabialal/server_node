from rest_framework import serializers
from .models import Product, Pipeline, Log

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  # or specify the fields you want to include

    def create(self, validated_data):
        db = self.context.get('db', 'default')  # Get the db from the context
        return Product.objects.using(db).create(**validated_data)

class PipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pipeline
        fields = '__all__'

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'





