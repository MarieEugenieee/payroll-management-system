from datetime import timedelta
from datetime import date

# Permissions Classes
from django.contrib.auth.mixins import LoginRequiredMixin

# Class-based View
from django.views.generic import TemplateView

# Models
from employee.models import EmployeeInfo
from reception.models import Attendance
from reception.models import SortLeave
from authority.models import OfficeTime
from authority.models import WeeklyOffday


class ReceptionView(LoginRequiredMixin, TemplateView):
    template_name = 'reception/reception.html'

    def get_context_data(self, **kwargs):
        # Initialize variables with default values
        total_employee = 0
        attend_today = 0
        start_time = None
        end_time = None
        day1 = None
        day2 = None
        
        try:
            # Database Queries
            total_employee = EmployeeInfo.objects.all().count()
            today = date.today()
            attend_today = Attendance.objects.filter(date=today).count()
            office_time_obj = OfficeTime.objects.last()
            if office_time_obj:
                start_time = office_time_obj.office_start
                end_time = office_time_obj.office_end

            weekly_offday_obj = WeeklyOffday.objects.last()
            if weekly_offday_obj:
                day1 = weekly_offday_obj.first_day
                day2 = weekly_offday_obj.second_day

        except Exception as e:
            print(f"Error occurred: {e}")

        # Prepare the context dictionary
        context = super().get_context_data(**kwargs)
        context["title"] = "Receptionist Home"
        context["total_employee"] = total_employee
        context["attend_today"] = attend_today
        context["absence_today"] = total_employee - attend_today
        context["Sort_leave"] = SortLeave.objects.filter(date=date.today()).count()
        context["late_present"] = Attendance.objects.filter(
            date=date.today(), late_present__gt=timedelta(minutes=30)
        ).count()
        context["office_start"] = start_time
        context["office_end"] = end_time
        context["off_day1"] = day1
        context["off_day2"] = day2

        return context
