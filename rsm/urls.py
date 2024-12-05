from django.urls import path
from . import views

urlpatterns = [
    
    path('sr/orders', views.sr_orders, name='sr_orders'),
    path('demands/demand', views.dealer_demand_check, name='dealer_demand_check'), 
    path('rsm/approved/<int:need_id>/', views.rsm_approved , name='rsm_approved'),  
   
]

