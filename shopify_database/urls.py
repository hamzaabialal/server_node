from django.urls import path
from .views import BulkProductInsertView, LogView, PipelineView

urlpatterns = [
    path('products/bulk-insert/', BulkProductInsertView.as_view(), name='bulk-insert'),
    path('log/', LogView.as_view(), name='log'),
    path('pipeline/', PipelineView.as_view(), name='pipeline'),
]
