from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Attendance)
admin.site.register(LeaveRequest)
admin.site.register(Payroll)
admin.site.register(PerformanceReview)
admin.site.register(Bonus) 
admin.site.register(Holiday) 
admin.site.register(LeaveBalance) 

