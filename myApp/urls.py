from django.contrib import admin
from django.urls import path
from myApp import views

urlpatterns = [
    path('', views.index , name='index'),
  
    
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('product/', views.product_view, name='product'),
    path('contact/', views.contact_view, name='contact'),
       
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
        
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-cart-item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('Account/', views.Account, name='Account'),
   
   


]