from django.urls import path
from . import views

urlpatterns = [
    path('', views.reg_log_page),
    path('dashboard', views.dashboard),
    path('register', views.register,name='register'),
    path('login', views.login,name='login'),

    path('shipments', views.shipments),
    path('create_shipment', views.create_shipment),
    path('shipments/<int:shipment_id>', views.view_shipment),#for details of shipment
    path('shipments/edit/<int:shipment_id>', views.edit_shipment),
    path('logout', views.logout),

]