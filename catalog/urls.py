from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.HomeListView.as_view(), name='home'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    # CRUD для продуктов
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Отмена публикации (для модераторов)
    path('product/<int:pk>/unpublish/', views.ProductUnpublishView.as_view(), name='product_unpublish'),

    # Просмотр продуктов по категориям
    path('category/<int:category_id>/', views.CategoryProductsView.as_view(), name='category_products'),
]