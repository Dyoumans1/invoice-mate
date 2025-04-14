from django.urls import path
from . import views 

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('clients/', views.client_index, name='client-index'),
    path('clients/<int:client_id>/', views.client_detail, name='client-detail'),
    path('clients/create/', views.ClientCreate.as_view(), name='client-create'),
    path('clients/<int:pk>/update/', views.ClientUpdate.as_view(), name='client-update'),
    path('clients/<int:pk>/delete/', views.ClientDelete.as_view(), name='client-delete'),


    path('invoices/', views.invoice_index, name='invoice-index'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice-detail'),
    path('invoices/create/', views.InvoiceCreate.as_view(), name='invoice-create'),
    path('invoices/<int:pk>/update/', views.InvoiceUpdate.as_view(), name='invoice-update'),
    path('invoices/<int:pk>/delete/', views.InvoiceDelete.as_view(), name='invoice-delete'),

    path('invoices/<int:invoice_id>/items/create/', views.ItemCreate.as_view(), name='item-create'),
    path('items/<int:pk>/update/', views.ItemUpdate.as_view(), name='item-update'),
    path('items/<int:pk>/delete/', views.ItemDelete.as_view(), name='item-delete'),

    path('invoices/<int:invoice_id>/pdf/', views.generate_pdf_invoice, name='invoice-pdf'),
]
