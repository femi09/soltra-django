from django.urls import path
from .views import ProductViewSet, ProductUpdateDeleteViewSet, ProductByUserView


urlpatterns = [
    path('', ProductViewSet.as_view(), name='product-list'),
    path('get-by-user', ProductByUserView.as_view(), name='product-list-by-user'),
    path('<str:id>', ProductUpdateDeleteViewSet.as_view(), name="product-details"),
    
]
