from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Attendance, LeaveRequest, Payroll, PerformanceReview, Bonus, Holiday
from .forms import LeaveRequestForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Attendance, LeaveRequest, Payroll
from .forms import AttendanceForm, LeaveRequestForm, PayrollForm
from django.contrib import messages
from django.utils.dateparse import parse_date

# HR/Manager Dashboard
@login_required
def hr_dashboard(request):
    return render(request, 'hr/dashboard.html')

# Attendance Management
from django.contrib.auth.models import User

@login_required
def attendance_list(request):
    attendances = Attendance.objects.all()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    user_id = request.GET.get('user')

    # Filter based on from_date and to_date
    if from_date:
        attendances = attendances.filter(date__gte=parse_date(from_date))
    if to_date:
        attendances = attendances.filter(date__lte=parse_date(to_date))
    if user_id:
        attendances = attendances.filter(user__id=user_id)

    users = User.objects.all()  # Fetch all users

    return render(
        request, 
        'hr/attendance_list.html', 
        {
            'attendances': attendances,
            'from_date': from_date,
            'to_date': to_date,
            'user_id': user_id,
            'users': users,
        }
    ) 
    
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta, date  

@login_required
def attendance_report(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    user_id = request.GET.get('user')

    # Parse date range
    if from_date and to_date:
        from_date = parse_date(from_date)
        to_date = parse_date(to_date)
    else:
        from_date = date.today() - timedelta(days=7)  # Default: last 7 days
        to_date = date.today()

    users = User.objects.all()
    report = []

    # If a user is selected, generate the report
    if user_id:
        try:
            selected_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            selected_user = None

        if selected_user:
            current_date = from_date
            user_attendance = Attendance.objects.filter(user=selected_user, date__range=(from_date, to_date))
            holidays = Holiday.objects.values_list('date', flat=True)  # List of holidays
            attendance_dict = {att.date: att for att in user_attendance}

            user_report = []
            present_count = 0
            half_day_count = 0

            while current_date <= to_date:
                att = attendance_dict.get(current_date)

                # Check if the day is a Friday or a holiday
                if current_date.weekday() == 4 or current_date in holidays:  # Friday is weekday 4
                    status = "Holiday"
                    total_hours = 0
                    late = False
                elif att:
                    # Check for Late status
                    late = False
                    if att.check_in_time and att.check_in_time > datetime.strptime("10:00", "%H:%M").time():
                        late = True

                    # Count Present and Half-Day statuses
                    if att.status == "Present":
                        present_count += 1
                    elif att.status == "Half-Day":
                        half_day_count += 1

                    # Calculate total work hours
                    if att.check_in_time and att.check_out_time:
                        work_duration = datetime.combine(date.min, att.check_out_time) - datetime.combine(date.min, att.check_in_time)
                        total_hours = round(work_duration.total_seconds() / 3600, 2)
                    else:
                        total_hours = 0

                    status = att.status
                else:
                    # No attendance for the day, mark as Absent
                    status = "Absent"
                    total_hours = 0
                    late = False

                user_report.append({
                    'date': current_date,
                    'status': status,
                    'check_in_time': att.check_in_time if att else None,
                    'check_out_time': att.check_out_time if att else None,
                    'total_hours': total_hours,
                    'late': late,
                })
                current_date += timedelta(days=1)

            report.append({
                'user': selected_user,
                'attendance': user_report,
                'present_count': present_count,
                'half_day_count': half_day_count,
            })

    return render(
        request,
        'hr/attendance_report.html',
        {
            'report': report,
            'from_date': from_date,
            'to_date': to_date,
            'users': users,
            'selected_user': user_id,
        }
    )
    
    

@login_required
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance record created successfully!')
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'hr/attendance_form.html', {'form': form})

@login_required
def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance record updated successfully!')
            return redirect('attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'hr/attendance_form.html', {'form': form})

@login_required
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    attendance.delete()
    messages.success(request, 'Attendance record deleted successfully!')
    return redirect('attendance_list')

# Leave Request Management
@login_required
def leave_requests_list(request):
    leave_requests = LeaveRequest.objects.all()
    return render(request, 'hr/leave_requests_list.html', {'leave_requests': leave_requests})

@login_required
def leave_request_update(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave request updated successfully!')
            return redirect('leave_requests_list')
    else:
        form = LeaveRequestForm(instance=leave_request)
    return render(request, 'hr/leave_request_form.html', {'form': form})

@login_required
def leave_request_delete(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    leave_request.delete()
    messages.success(request, 'Leave request deleted successfully!')
    return redirect('leave_requests_list')

# Payroll Management
@login_required
def payroll_list(request):
    payrolls = Payroll.objects.all()
    return render(request, 'hr/payroll_list.html', {'payrolls': payrolls})

@login_required
def payroll_create(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll record created successfully!')
            return redirect('payroll_list')
    else:
        form = PayrollForm()
    return render(request, 'hr/payroll_form.html', {'form': form})

@login_required
def payroll_update(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if request.method == 'POST':
        form = PayrollForm(request.POST, instance=payroll)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll record updated successfully!')
            return redirect('payroll_list')
    else:
        form = PayrollForm(instance=payroll)
    return render(request, 'hr/payroll_form.html', {'form': form})

@login_required
def payroll_delete(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    payroll.delete()
    messages.success(request, 'Payroll record deleted successfully!')
    return redirect('payroll_list')





###########For User########################
# # Dashboard View
# @login_required
# def dashboard(request):
#     profile = request.user.profile
#     context = {
#         'profile': profile,
#         'attendance_count': Attendance.objects.filter(user=request.user).count(),
#         'leave_count': LeaveRequest.objects.filter(user=request.user).count(),
#         'payroll_count': Payroll.objects.filter(user=request.user).count(),
#     }
#     return render(request, 'hrm/dashboard.html', context)

# # Attendance List View
# @login_required
# def attendance_list(request):
#     attendance_records = Attendance.objects.filter(user=request.user).order_by('-date')
#     return render(request, 'hrm/attendance_list.html', {'attendance_records': attendance_records})

# Leave Request List and Create View
@login_required
def leave_requests(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            messages.success(request, "Leave request submitted successfully!")
            return redirect('leave_requests')
    else:
        form = LeaveRequestForm()

    leave_requests = LeaveRequest.objects.filter(user=request.user).order_by('-requested_at')
    context = {'form': form, 'leave_requests': leave_requests}
    return render(request, 'hrm/leave_requests.html', context)

# # Payroll View
# @login_required
# def payroll_list(request):
#     payrolls = Payroll.objects.filter(user=request.user).order_by('-year', '-month')
#     return render(request, 'hrm/payroll_list.html', {'payrolls': payrolls})

# # Performance Review View
# @login_required
# def performance_reviews(request):
#     reviews = PerformanceReview.objects.filter(user=request.user).order_by('-review_date')
#     return render(request, 'hrm/performance_reviews.html', {'reviews': reviews})

# # Bonus List View
# @login_required
# def bonus_list(request):
#     bonuses = Bonus.objects.filter(user=request.user).order_by('-issued_date')
#     return render(request, 'hrm/bonus_list.html', {'bonuses': bonuses})


