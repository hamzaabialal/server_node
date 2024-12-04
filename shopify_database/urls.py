from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, aggregate_search, sync_databases

# Create a router and register the ProductViewSet
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

# Now the `search` action and `bulk-insert` will be automatically included in the routes
urlpatterns = [
    path('aggregate_search/', aggregate_search, name='aggregate-search'),
    path('sync_databases/', sync_databases),

              ] + router.urls  # Add the router URLs to the urlpatterns