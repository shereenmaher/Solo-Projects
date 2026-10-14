from django.urls import path
from . import views

urlpatterns = [
    path('', views.reg_log_page, name='reg_log_page'),
    path('dashboard', views.shipments, name='dashboard'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('shipments', views.shipments, name='shipments'),
    path('create_shipment', views.create_shipment, name='create_shipment'),
    path('shipments/<int:shipment_id>',views.view_shipment,name='view_shipment'),
    path('shipments/edit/<int:shipment_id>',views.edit_shipment,name='edit_shipment'),
    path('logout', views.logout, name='logout'),
]
