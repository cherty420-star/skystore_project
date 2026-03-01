from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('post/<int:pk>/', views.BlogDetailView.as_view(), name='post_detail'),
    path('create/', views.BlogCreateView.as_view(), name='post_create'),
    path('update/<int:pk>/', views.BlogUpdateView.as_view(), name='post_update'),
    path('delete/<int:pk>/', views.BlogDeleteView.as_view(), name='post_delete'),
]