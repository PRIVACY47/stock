from django.contrib import admin
from django.urls import path
from stock_man import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin/', admin.site.urls),
    
    path('reset_password/', views.reset_password, name='reset_password'),
    path('edit_user/', views.edit_user, name='edit_user'),
    path('change_status/', views.change_status, name='change_status'),
    path('create_user/', views.create_user, name='create_user'),
    path('search_user/', views.search_user, name='search_user'),
    path('register/', views.register, name='register'),
    path('receive_stock/', views.receive_stock, name='receive_stock'),
    path('issue_stock/', views.issue_stock, name='issue_stock'),
    path('issue_stock_view/', views.issue_stock_view, name='issue_stock_view'),
    path('check_inventory/', views.check_inventory, name='check_inventory'),
    path('add_item_view/', views.add_item_view, name='add_item_view'),
    path('receive_stock_view/', views.receive_stock_view, name='receive_stock_view'),
    path('request_stock/', views.request_stock, name='request_stock'),
    path('request_stock_view/', views.request_stock_view, name='request_stock_view'),
    path('stock_master/', views.stock_master, name='stock_master'),
    path('addtocategory_request/', views.addtocategory_request, name='addtocategory_request'),
    path('addtocategory/', views.addtocategory, name='addtocategory'),
    path('edit_category/', views.edit_category, name='edit_category'),
    path('generate_qr_code_view/', views.generate_qr_code_view, name='generate_qr_code_view'),
    path('generate_qr_code/', views.generate_qr_code, name='generate_qr_code'),
    path('generate_pdf_with_qr_id/', views.generate_pdf_with_qr_id, name='generate_pdf_with_qr_id'),
    path('issue_receive/', views.issue_receive, name='issue_receive'),
    path('generate_pdf_with_qr_codes/', views.generate_pdf_with_qr_codes, name='generate_pdf_with_qr_codes'),
    path('generate_pdf_qr_receive/', views.generate_pdf_qr_receive, name='generate_pdf_qr_receive'),
    path('get_items/', views.get_items, name='get_items'),
    path('fetch_item_qty/', views.fetch_item_qty, name='fetch_item_qty'),
    path('modify_qty/', views.modify_qty, name='modify_qty'),
    path('edit_qr/', views.edit_qr, name='edit_qr'),
    path('delete_item/', views.delete_item, name='delete_item'),
    path('qr_code/', views.qr_code, name='qr_code'),
    path('check_qr/', views.check_qr, name='check_qr'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]