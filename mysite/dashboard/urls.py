from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard_page, name="dashboard"),
    path('login/', views.dashboard_login, name="login"),
    path('logout/', views.dashboard_logout, name="logout"),

    path('user/', views.user_list, name="user_list"),
    path('user/add/', views.user_create, name="user_add"),
    path('user/<int:pk>/edit/', views.user_edit, name="user_edit"),
    path('user/<int:pk>/delete/', views.user_delete, name="user_delete"),

    path("status/<int:pk>/<int:status>", views.status, name="status"),
    path("status/list/", views.order_list, name="order_list"),

    path('category/', views.category_list, name="category_list"),
    path('category/add/', views.category_create, name="category_add"),
    path('category/<int:pk>/edit', views.category_edit, name="category_edit"),
    path('category/<int:pk>/delete/', views.category_delete, name="category_delete"),

    path('product/', views.product_list, name="product_list"),
    path('product/add/', views.product_create, name="product_add"),
    path('product/<int:pk>/edit', views.product_edit, name="product_edit"),
    path('product/<int:pk>/delete/', views.product_delete, name="product_delete"),

]
