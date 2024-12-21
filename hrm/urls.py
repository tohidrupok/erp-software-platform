from django.urls import path
from . import views

urlpatterns = [
    # HR/Manager Dashboard
    path('dashboard/', views.hr_dashboard, name='hr_dashboard'),

    # Attendance Management
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/update/<int:pk>/', views.attendance_update, name='attendance_update'),
    path('attendance/delete/<int:pk>/', views.attendance_delete, name='attendance_delete'),
    path('attendance-report/', views.attendance_report, name='attendance_report'),

    # Leave Request Management
    path('leave-list/', views.leave_requests_list, name='leave_requests_list'),
    path('approve_leave/<int:pk>/', views.approve_leave, name='approve_leave'),
    path('reject_leave/<int:pk>/', views.reject_leave, name='reject_leave'),
    path('leave-request/', views.leave_requests, name='leave_requests'),
    path('leave-request/update/<int:pk>/', views.leave_request_update, name='leave_request_update'),
    path('leave-request/delete/<int:pk>/', views.leave_request_delete, name='leave_request_delete'),

    # Payroll Management
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/create/', views.payroll_create, name='payroll_create'),
    path('payroll/update/<int:pk>/', views.payroll_update, name='payroll_update'),
    path('payroll/delete/<int:pk>/', views.payroll_delete, name='payroll_delete'),

    
  
     
    
    
    # path('', views.dashboard, name='dashboard'),  
    # path('attendance/', views.attendance_list, name='attendance_list'), 
    path('leave-requests/', views.leave_requests, name='leave_request_create'), 
    # path('payroll/', views.payroll_list, name='payroll_list'),  
    # path('performance-reviews/', views.performance_reviews, name='performance_reviews'), 
    # path('bonuses/', views.bonus_list, name='bonus_list'),
]
