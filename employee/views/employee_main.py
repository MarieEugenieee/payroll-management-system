from django.urls import reverse_lazy
from django.contrib import messages

# Permissions Classes
from django.contrib.auth.mixins import LoginRequiredMixin
from employee.permission import EmployeePassesTestMixin

# Generic Views
from django.views.generic import TemplateView
from datetime import datetime

from authority.models import PayrollMonth
from authority.models import LeaveApplication
from authority.models import MonthlyPermitedLeave
from authority.models import PermitedSortLeave
from authority.models import OfficeTime
from authority.models import Notice
from authority.models import WeeklyOffday
from authority.models import PermitedLatePresent
from reception.models import Attendance
from reception.models import SortLeave

class EmployeeHomeView(LoginRequiredMixin, EmployeePassesTestMixin, TemplateView):
    template_name = 'employee/employee.html'

    def get_context_data(self, **kwargs):
        # Initialize variables with default values
        current_month_name = datetime.now().strftime('%B')
        current_year_name = datetime.now().strftime('%Y')
        total_leave = 0
        this_month_attendance = 0
        late_present = 0
        permited_leave_days = 0
        permited_late_present = 0
        sort_leave = 0
        permited_sort_leave = 0
        start_time = None
        end_time = None
        day1 = None
        day2 = None

        try:
            # Payroll Month and Attendance Data
            month_obj = PayrollMonth.objects.get(month=current_month_name[0:3], year=current_year_name)
            from_date = month_obj.from_date
            to_date = datetime.today().date()
            this_month_attendance = Attendance.objects.filter(attendance_of=self.request.user.employee_info, date__range=[from_date, to_date]).count()
            total_leave = LeaveApplication.objects.filter(application_of=self.request.user, is_active=True, approved_status=True, leave_from__range=[from_date, to_date]).count()

            # Late Present Data
            permi_late_obj = PermitedLatePresent.objects.last()
            if permi_late_obj:
                late_present = Attendance.objects.filter(attendance_of=self.request.user.employee_info, date__range=[from_date, to_date], late_present__gt=permi_late_obj.peremited_time).count()
                permited_late_present = permi_late_obj.permited_days

            # Permitted Leave Data
            permited_leave_obj = MonthlyPermitedLeave.objects.get(leave_month=current_month_name[0:3])
            permited_leave_days = permited_leave_obj.permited_days

            # Sort Leave Data
            permited_sort_leave_obj = PermitedSortLeave.objects.last()
            if permited_sort_leave_obj:
                sort_leave = SortLeave.objects.filter(ticket_for=self.request.user.employee_info, date__range=[from_date, to_date]).count()
                permited_sort_leave = permited_sort_leave_obj.permited_days

            # Office Time Data
            office_time_obj = OfficeTime.objects.last()
            if office_time_obj:
                start_time = office_time_obj.office_start
                end_time = office_time_obj.office_end

            # Weekly Offday Data
            weekly_offday_obj = WeeklyOffday.objects.last()
            if weekly_offday_obj:
                day1 = weekly_offday_obj.first_day
                day2 = weekly_offday_obj.second_day

        except Exception as e:
            print(f"Error occurred: {e}")

        # Prepare the context dictionary
        context = super().get_context_data(**kwargs)
        context["title"] = "Employee Home"
        context["total_attendance"] = this_month_attendance
        context["current_month"] = f"{current_month_name[0:3]},{current_year_name}"
        context["leave"] = total_leave
        context["leave_permited"] = permited_leave_days
        context["late"] = late_present
        context["late_permited"] = permited_late_present
        context["half_day"] = sort_leave
        context["half_day_permited"] = permited_sort_leave
        context["office_start"] = start_time
        context["office_end"] = end_time
        context["off_day1"] = day1
        context["off_day2"] = day2
        context["notices"] = Notice.objects.filter(is_active=True).order_by('-id')[:5]

        return context
