from django.db import models

class Pipeline(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

from django.db import models

from django.db import models

class Product(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    image_url = models.URLField(null=True)
    price = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    niche = models.CharField(max_length=100)



    class Meta:
        indexes = [
            models.Index(fields=['title']),
        ]

class Log(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='logs')
    log_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
