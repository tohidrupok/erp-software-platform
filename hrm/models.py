from django.db import models
from django.contrib.auth.models import User


class Holiday(models.Model):
    date = models.DateField(unique=True)  
    name = models.CharField(max_length=255)  

    class Meta:
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"
        ordering = ['date']  

    def __str__(self):
        return f"{self.name} - {self.date}"
 
 
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=[
            ('Present', 'Present'),
            ('Absent', 'Absent'),
            ('Leave', 'Leave'),
            ('Half-Day', 'Half-Day'),
        ],
    )
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.status})"

class LeaveRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending',
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Leave: {self.user.username} ({self.status})"
    

from django.utils.timezone import now 

class LeaveBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_balance")
    year = models.IntegerField(default=now().year)  
    total_leaves = models.IntegerField(default=24)  
    used_leaves = models.IntegerField(default=0)   
    carry_forward = models.IntegerField(default=0) 

    def remaining_leaves(self):
        """Calculate remaining leaves."""
        return self.total_leaves + self.carry_forward - self.used_leaves

    def __str__(self):
        return f"{self.user.username} - {self.year} Leave Balance"  
    
    
    
class Payroll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically calculate net salary
        self.net_salary = self.basic_salary + self.allowances - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payroll: {self.user.username} - {self.month}/{self.year}"


class PerformanceReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    review_date = models.DateField()
    reviewer = models.CharField(max_length=100)
    comments = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)]) 

    def __str__(self):
        return f"Performance Review: {self.user.username} ({self.rating}/5)"


class Bonus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    issued_date = models.DateField()

    def __str__(self):
        return f"Bonus: {self.user.username} ({self.amount})"
