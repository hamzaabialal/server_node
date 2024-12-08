from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ScrapeShopifyData, aggregate_search, Dashboard1TemplateView, sync_databases, DashboardTemplateView

# Create a router and register the ProductViewSet
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

# Now the `search` action and `bulk-insert` will be automatically included in the routes
urlpatterns = [
    path('aggregate_search/', aggregate_search, name='aggregate-search'),
    path('sync_databases/', sync_databases),
    path('dashboardview/', DashboardTemplateView.as_view(), name='dashboard-view'),
    path('dashboard1/', Dashboard1TemplateView.as_view(), name='dashboard1-view'),
    path('scraoeproducts/', ScrapeShopifyData.as_view(),  name='scrape-products')

              ] + router.urls  # Add the router URLs to the urlpatterns