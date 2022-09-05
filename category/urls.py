from django.urls import path
from category.views import CategoryViewSet


urlpatterns = [
    path('create', CategoryViewSet.as_view(
        {'post': 'create'}), name='create_category'),
    path('get-all-categories',
         CategoryViewSet.as_view({'get': 'list'}), name='category_list'),
    path('update/<str:id>',
         CategoryViewSet.as_view({'put': 'update'}), name='update_category'),
    path('<str:id>', CategoryViewSet.as_view({"get":"retrieve"}), name='get_category'),
    path('delete/<str:id>', CategoryViewSet.as_view({"delete":"delete"}), name='delete_category')
]
