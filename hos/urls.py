from django.urls import path
from . import views

urlpatterns = [
    
    path('hos/check', views.check, name='hos_check'),
    path('hos/dealer/demand', views.hos_dealer_demand_check, name='hos_dealer_demand'), 
    path('hos/approved/<int:need_id>/', views.hos_approved , name='hos_approved'),  

   
]

