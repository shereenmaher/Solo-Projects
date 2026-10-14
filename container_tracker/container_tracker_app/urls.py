from django.urls import path
from . import views

urlpatterns = [
    path('', views.reg_log_page),
    path('dashboard', views.dashboard),
    path('login', views.login),

    path('shipments', views.shipments),
    path('create_shipment', views.create_shipment),
    path('shipments/<int:shipment_id>', views.view_shipment),#for details of show
    path('shipments/edit/<int:shipment_id>', views.edit_show),
    path('logout', views.logout),

]