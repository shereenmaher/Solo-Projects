from django.urls import path
from . import views


urlpatterns = [

    # Register / Login
    path(
        '',
        views.reg_log_page,
        name='reg_log_page'
    ),

    path(
        'register',
        views.register,
        name='register'
    ),

    path(
        'login',
        views.login,
        name='login'
    ),


    # Dashboard
    path(
        'dashboard',
        views.shipments,
        name='dashboard'
    ),


    # Create Shipment
    path(
        'create_shipment',
        views.create_shipment,
        name='create_shipment'
    ),


    # Shipment Details
    path(
        'shipments/<int:shipment_id>',
        views.view_shipment,
        name='view_shipment'
    ),


    # Edit Shipment
    path(
        'shipments/edit/<int:shipment_id>',
        views.edit_shipment,
        name='edit_shipment'
    ),


    # Shipment History
    path(
        'shipments/<int:shipment_id>/history',
        views.shipment_history,
        name='shipment_history'
    ),


    # Refresh Shipment
    path(
        'shipments/<int:shipment_id>/refresh',
        views.refresh_shipment,
        name='refresh_shipment'
    ),


    # Shipment Documents
    path(
        'shipments/<int:shipment_id>/documents',
        views.edit_shipment_documents,
        name='edit_shipment_documents'
    ),


    # Landed Cost
    path(
        'shipments/<int:shipment_id>/landed-cost',
        views.edit_landed_cost,
        name='edit_landed_cost'
    ),


    # Logout
    path(
        'logout',
        views.logout,
        name='logout'
    ),
]