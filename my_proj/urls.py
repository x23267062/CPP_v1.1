"""
URL configuration for my_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from orders import views

urlpatterns = [
    path('admin/', admin.site.urls),
#    path('login/', views.login_view, name='login'),
    path('order/', views.place_order, name='place_order'),
    path('order-success/', views.order_success, name='order_success'),
    path('track_home/',views.track_home, name='track_home'),
    path('ship_now/',views.ship_now, name='ship_now'),
    path('login_view/', views.login_view, name='login_view'),
    path('signup_view/', views.signup_view, name='signup_view'),
    path('',views.user_login, name='user_login'),
    path('order_list/',views.order_list, name='order_list'),
    path('place_order/', views.place_order, name='place_order'),
    path('delete/<int:index>/', views.delete, name='delete'),
    path('logout/', views.logout_view, name='logout'),
    #path('',views.user_login, name='user_login'),
]