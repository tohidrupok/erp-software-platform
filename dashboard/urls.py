from django.urls import path
from . import views

urlpatterns = [
    path('base/', views.base, name='base'),
    path('index/', views.index, name='dashboard-index'),
    
    path('add-shope/', views.shops, name='add-shope'), 
    path('daily-report/', views.daily_report, name='daily_report'),
    path('sr-order/', views.dealer_orders_view, name='sr-order'),

    path('get-districts/', views.get_districts, name='get-districts'),
    path('get-thanas/', views.get_thanas, name='get-thanas'),
    path('get-areas/', views.get_areas, name='get-areas'), 


    path('demand/', views.demand , name ='demand'),
    path('demand/check/', views.demand_request_check, name='demand_check'),

    path('offer/active/', views.active_offer_list, name='active_offer_list'), 
    path('order/manage/', views.order_manage , name='order_manage'), 
    path('order/<int:pk>/edit/', views.edit_order, name='edit_order'),
    path('order/<int:pk>/delete/', views.delete_order, name='delete_order'),

    path('reached/<int:need_id>/', views.reached_product, name='reached_product'),


    path('dealear/stocks/', views.user_stocks, name='user_stocks'),
    path('demand/<int:pk>/edit/', views.edit_demand, name='edit_demand'),
    path('demand/<int:pk>/delete/', views.delete_demand, name='delete_demand'),
    
    path('dealer/approved/<int:need_id>/', views.dealer_approved , name='dealer_approved'),  

    
]
