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

# models.py
from django.db import models

class Product(models.Model):
    url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True, default='No title')
    description = models.TextField(null=True, blank=True, default="")
    image_url = models.URLField(null=True, blank=True,default="")
    price = models.CharField(max_length=100, null=True, blank=True, default="")
    city = models.CharField(max_length=100, null=True, blank=True, default="")
    country = models.CharField(max_length=100, null=True, blank=True, default="")
    niche = models.CharField(max_length=100, null=True, blank=True , default="")

    def __str__(self):
        return self.title



    class Meta:
        indexes = [
            models.Index(fields=['title']),
        ]

class Log(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='logs')
    log_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
