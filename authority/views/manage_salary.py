from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from datetime import timedelta


# Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from authority.permission import AdminPassesTestMixin


# Django Generic Views
from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

# Models
from employee.models import EmployeeInfo
from employee.models import EmployeeSalary
from employee.models import MonthlySalary
from employee.models import FestivalBonus
from authority.models import PayrollMonth
from authority.models import MonthlyOffDay
from authority.models import MonthlyHoliday
from authority.models import PermitedLatePresent
from authority.models import MonthlyPermitedLeave
from authority.models import PermitedSortLeave
from reception.models import Attendance
from reception.models import SortLeave

# Forms
from employee.forms import MonthlySalaryForm

# Filters
from authority.filters import SalaryEmployeeFilters
from authority.filters import EmployeeMonthlySalaryFilter
from authority.filters import CalculatedMonthlySalaryFilter



class EmployeeSalaryListView(LoginRequiredMixin, AdminPassesTestMixin, ListView):

    model = EmployeeInfo
    queryset = EmployeeInfo.objects.filter(is_active=True)
    filterset_class = SalaryEmployeeFilters
    template_name = 'authority/salary_employee_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Employee List"
        context["form"] = MonthlySalaryForm
        context["employees"] = self.filterset_class(self.request.GET, queryset=self.queryset)
        return context

class MonthilySalaryCalculationView(LoginRequiredMixin, AdminPassesTestMixin, CreateView):
    
    model = MonthlySalary
    form_class = MonthlySalaryForm
    template_name = 'authority/monthily_salary.html'
    success_url = reverse_lazy('authority:monthly_salary_details', kwargs={'pk': 0})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Monthily Salary Calculation" 
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['other_pk'] = self.kwargs['pk']
        return initial
    
    def form_valid(self, form):
        try:
            # Get salary_month and employee details
            salary_month = form.cleaned_data.get('salary_month')
            employee = EmployeeInfo.objects.get(id=self.kwargs['pk'])
            salary = EmployeeSalary.objects.get(salary_of=employee)
           

            # Check if salary has already been calculated for the given month
            if MonthlySalary.objects.filter(salary_month=salary_month, salary_employee=employee).exists():
                obj_slary = MonthlySalary.objects.get(salary_month=salary_month, salary_employee=employee, is_active=True)
                messages.warning(self.request, "Salary already calculated in this month")
                return redirect('authority:monthly_salary_details', pk=obj_slary.id)
           
            # Calculate various allowances and salary components
            conveyance = float(salary.basic_salary) * float(salary.conveyance or 0) / 100
            food_allowance = float(salary.basic_salary) * float(salary.food_allowance or 0) / 100
            medical_allowance = float(salary.basic_salary) * float(salary.medical_allowance or 0) / 100
            house_rent = float(salary.basic_salary) * float(salary.house_rent or 0) / 100
            mobile_allowance = float(salary.basic_salary) * float(salary.mobile_allowance or 0) / 100

            festival_bonus = 0
            if form.cleaned_data.get('festival_bonus') is not None:
                value = form.cleaned_data.get('festival_bonus')
                festival = FestivalBonus.objects.get(festival_name=value)
                festival_bonus = float(salary.basic_salary) * float(festival.bonus_percentage or 0) / 100

            salary_fields = (conveyance, food_allowance, medical_allowance, house_rent, mobile_allowance, festival_bonus)
            total_salary_value = float(salary.basic_salary) + float(sum(salary_fields))

            try:
                month = PayrollMonth.objects.get(month=salary_month.month)

                # Ensure month.total_days is an integer
                if isinstance(month.total_days, int):
                    days = month.total_days
                else:
                    print(f"Warning: Invalid 'total_days' type: {type(month.total_days)}. Defaulting to 0.")
                    days = 0

                print(f"PayrollMonth for {salary_month.month} found with {days} days.")

            except PayrollMonth.DoesNotExist:
                days = 0
                print(f"PayrollMonth for {salary_month.month} does not exist. Defaulting 'days' to 0.")

            # Get and calculate Permitted Leave and Sort Leave deductions
            try:
                permited_leave = MonthlyPermitedLeave.objects.get(leave_month=month.month)
                permited_leave_days = permited_leave.permited_days or 0
                permited_leave_salary_diduct = permited_leave.salary_diduction or 0
            except MonthlyPermitedLeave.DoesNotExist:
                permited_leave_days = 0
                permited_leave_salary_diduct = 0
                print(f"Error: No MonthlyPermitedLeave found for month {month.month}")

            # Get PermitedLatePresent and PermitedSortLeave
            permited_latepresent = PermitedLatePresent.objects.first()
            if permited_latepresent is None:
                print("Error: No PermitedLatePresent record found.")
                late_permited_time = 0
                late_permited_days = 0
                late_present_salary_diduct = 0
            else:
                late_permited_time = permited_latepresent.peremited_time or 0
                late_permited_days = permited_latepresent.permited_days or 0
                late_present_salary_diduct = permited_latepresent.salary_deduction or 0

            permited_sortleave = PermitedSortLeave.objects.first()
            if permited_sortleave is None:
                print("Error: No PermitedSortLeave record found.")
                permited_sortleave_days = 0
                sortleave_salary_diduct = 0
            else:
                permited_sortleave_days = permited_sortleave.permited_days or 0
                sortleave_salary_diduct = permited_sortleave.salary_deduction or 0

            # Calculating off days and holidays
            off_day = 0
            if MonthlyOffDay.objects.filter(month=month).exists():
                day = MonthlyOffDay.objects.get(month=month)
                off_day = day.total_offday or 0
        
            holiday = 0
            if MonthlyHoliday.objects.filter(holiday_month=month).exists():
                holiday = MonthlyHoliday.objects.filter(holiday_month=month, is_active=True).count() or 0
            
            # Calculate attendance and deductions
            try:
                month_attendance = Attendance.objects.filter(attendance_of=employee, date__range=[month.from_date, month.to_date]).count() or 0
                late_present = Attendance.objects.filter(attendance_of=employee, date__range=[month.from_date, month.to_date], late_present__gt=late_permited_time).count() or 0
                sort_leave = SortLeave.objects.filter(ticket_for=employee, date__range=[month.from_date, month.to_date]).count() or 0
             
            except Exception as e:
                print(f"Error while calculating attendance and deductions: {str(e)}")
                month_attendance = 0
                late_present = 0
                sort_leave = 0

            print(f"Month Attendance: {month_attendance}, Late Present: {late_present}, Sort Leave: {sort_leave}")

            # Calculate salary per day
            per_day_basic_salary = float(salary.basic_salary) / float(days or 1)

            print(f"basic per day: {per_day_basic_salary}")
           
            # Calculate Total Salary Deduction for late presence
            salary_diduct_for_late_present = 0
            late = 0
            if late_present >= late_permited_days:
                late = int(late_present - late_permited_days)
                diduct_salary = float(per_day_basic_salary) * float(late_present_salary_diduct or 0) / 100
                salary_diduct_for_late_present = diduct_salary * late

            # Total Salary Deduction for extra leave
            extra_leave = float(days - (month_attendance + holiday + permited_leave_days + off_day))
            diduct_per_day = float(per_day_basic_salary) * float(permited_leave_salary_diduct or 0) / 100
            salary_diduct_for_leave = diduct_per_day * extra_leave

            # Sort Leave Deduction
            salary_diduct_for_sort_leave = 0
            month_sort_leave = 0
            if sort_leave >= permited_sortleave_days:
                month_sort_leave = int(sort_leave - permited_sortleave_days)
                diduct_salary = float(per_day_basic_salary) * float(sortleave_salary_diduct or 0) / 100
                salary_diduct_for_sort_leave = diduct_salary * month_sort_leave

            total_salary_diduct = float(salary_diduct_for_late_present + salary_diduct_for_leave + salary_diduct_for_sort_leave)

            # Saving form data
            if form.is_valid():
                form_obj = form.save(commit=False)
                form_obj.salary_employee = employee
                form_obj.prepared_by = self.request.user
                form_obj.salary_of = salary
                form_obj.total_conveyance = conveyance
                form_obj.total_food_allowance = food_allowance
                form_obj.total_medical_allowance = medical_allowance
                form_obj.total_house_rent = house_rent
                form_obj.total_mobile_allowance = mobile_allowance
                form_obj.total_bonus = festival_bonus
                form_obj.total_salary = total_salary_value
                form_obj.late_present_diduct = salary_diduct_for_late_present
                form_obj.extra_leave_diduct = salary_diduct_for_leave
                form_obj.sort_leave_diduct = salary_diduct_for_sort_leave
                form_obj.total_diduct = total_salary_diduct
                form_obj.total_absence = extra_leave
                form_obj.exatra_sort_leave = month_sort_leave
                form_obj.extra_late_present = late
                form_obj.save()
                messages.success(self.request, "Salary Added Successfully")
                self.object = form_obj

            self.success_url = reverse_lazy('authority:monthly_salary_details', kwargs={'pk': self.object.id})
            return super().form_valid(form)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Something went worng try aging!")
        return super().form_invalid(form)


class EmployeeMonthlySalaryListView(LoginRequiredMixin, AdminPassesTestMixin, ListView):
     model = MonthlySalary
     queryset = MonthlySalary.objects.filter(is_active=True).order_by('-id')
     filterset_class = EmployeeMonthlySalaryFilter
     template_name = 'authority/employee_salary_list.html'

     def get_initial(self):
        initial = super().get_initial()
        initial['other_pk'] = self.kwargs['pk']
        return initial
     
     def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(salary_employee__id=self.kwargs['pk'])
        

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context["title"] = "Employee Salary List" 
         context["employee"] = EmployeeInfo.objects.filter(id=self.kwargs['pk']).first()
         context["salarys"] = self.filterset_class(self.request.GET, queryset=self.get_queryset())
         return context
     

class MonthlyCalculatedSalaryListView(LoginRequiredMixin, AdminPassesTestMixin, ListView):
    model = MonthlySalary
    queryset = MonthlySalary.objects.filter(is_active=True).order_by('-id')
    filterset_class = CalculatedMonthlySalaryFilter
    template_name = 'authority/calculated_salary_list.html'

    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context["title"] = "Calculated Salary List"
         context["salarys"] = self.filterset_class(self.request.GET, queryset=self.get_queryset())
         return context


class MonthlySalaryDetailsView(LoginRequiredMixin, AdminPassesTestMixin, DetailView):
    model = MonthlySalary
    context_object_name = 'salary'
    template_name = 'authority/salary_details.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        return obj

    def get_context_data(self, **kwargs):
        query_obj = self.get_object()
        total_salary = query_obj.total_salary
        total_diduct = query_obj.total_diduct
        context = super().get_context_data(**kwargs)
        context["title"] = "Monthly Salary Details" 
        context["total_salary_pay"] =round(total_salary-total_diduct)

        return context
    
    

class UpdateCalculatedSalaryView(LoginRequiredMixin, AdminPassesTestMixin, UpdateView):
    model = MonthlySalary
    form_class = MonthlySalaryForm
    template_name = 'authority/update_calculated_salary.html'
    success_url = reverse_lazy('authority:calculated_salary_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Calculated Salary"
        context["salary"] = MonthlySalary.objects.get(id=self.kwargs['pk']) 
        return context

    def form_valid(self, form):
        try:
            salary_month = form.cleaned_data.get('salary_month')

            calculated_salary=MonthlySalary.objects.get(id=self.kwargs['pk'])

            employee = calculated_salary.salary_employee
        

            salary = EmployeeSalary.objects.get(salary_of=calculated_salary.salary_employee)
        

            plus_minus_bonus=0
            if form.cleaned_data.get('festival_bonus') is not None:
                value = form.cleaned_data.get('festival_bonus')
                fastival= FestivalBonus.objects.get(festival_name=value)
                plus_minus_bonus =float(salary.basic_salary)*float(fastival.bonus_percentage/100)
            
           
            if form.cleaned_data.get('festival_bonus') is None:
               plus_minus_bonus =  float(calculated_salary.total_bonus)- float(calculated_salary.total_bonus)

            
            # Total Salary Diduction 

            # Salary month
            month = PayrollMonth.objects.get(month=salary_month.month)
            days = month.total_days
            
        
            # Permited Late present
            permited_latepresent = PermitedLatePresent.objects.first()
            late_permited_time = permited_latepresent.peremited_time
            late_permited_days = permited_latepresent.permited_days
            late_present_salary_diduct = permited_latepresent.salary_diduction

            # Permited Sort Leave
            permited_sortleave = PermitedSortLeave.objects.first()
            permited_sortleave_days = permited_sortleave.permited_days
            sortleave_salary_diduct = permited_sortleave.salary_diduction

            # Permited Leave 
            permited_leave = MonthlyPermitedLeave.objects.get(leave_month=month.month)
            permited_leave_days = permited_leave.permited_days
            permited_leave_salary_diduct = permited_leave.salary_diduction

            # Calculated Salary month total off day
            off_day = 0
            if MonthlyOffDay.objects.filter(month=month).exists():
                day = MonthlyOffDay.objects.get(month=month)
                off_day = day.total_offday

            # Calculated Salary month total holiday
            holiday = 0
            if MonthlyHoliday.objects.filter(holiday_month=month).exists():
                holiday = MonthlyHoliday.objects.filter(holiday_month=month, is_active=True).count()
            
            # Total Attendance
            month_attendance = Attendance.objects.filter(attendance_of= employee , date__range=[month.from_date,month.to_date]).count()

            # Total Late Present
            late_present = Attendance.objects.filter(attendance_of= employee , date__range=[month.from_date,month.to_date], late_present__gt=late_permited_time).count()
            
            # Total Sortleave
            sort_leave = SortLeave.objects.filter(ticket_for=employee, date__range=[month.from_date,month.to_date], ).count()

            # Salary of a employee for each day
            per_day_basic_salary = (salary.basic_salary/days)
            
            # Total Salary Diduct for late peresent in a month
            salary_diduct_for_late_present = 0
            late = 0
            if late_present > late_permited_days:
                late=int(late_present-late_permited_days)
                diduct_salary = float(per_day_basic_salary)*float(late_present_salary_diduct/100)
                salary_diduct_for_late_present =diduct_salary*late

            # Total Salary Diduct for the extra Leave
            extra_leave = (days-(month_attendance+holiday+permited_leave_days+off_day))
            diduct_per_day = float(per_day_basic_salary)*float(permited_leave_salary_diduct/100)
            salary_diduct_for_leave = (diduct_per_day*extra_leave)

            # Sort Leave Salary Diduction
            salary_diduct_for_sort_leave = 0
            month_sort_leave = 0
            if sort_leave>permited_leave_days:
                month_sort_leave = (sort_leave-permited_sortleave_days)
                print(month_sort_leave)
                diduct_salary = float(per_day_basic_salary)*float(sortleave_salary_diduct/100)
                salary_diduct_for_sort_leave = (diduct_salary*month_sort_leave)
            
            total_salary_diduct = (salary_diduct_for_late_present+salary_diduct_for_leave+salary_diduct_for_sort_leave)
               
        
            if form.is_valid():
                form_obj = form.save(commit=False)

                if calculated_salary.festival_bonus is None:
                    form_obj.total_bonus = plus_minus_bonus
                    form_obj.total_salary = calculated_salary.total_salary+form_obj.total_bonus

                if calculated_salary.festival_bonus is not None:
                    form_obj.total_bonus = form_obj.total_bonus-plus_minus_bonus
                    form_obj.total_salary =  calculated_salary.total_salary - form_obj.total_bonus
                
                form_obj.late_present_diduct = salary_diduct_for_late_present
                form_obj.extra_leave_diduct = salary_diduct_for_leave
                form_obj.sort_leave_diduct = salary_diduct_for_sort_leave
                form_obj.total_diduct = total_salary_diduct
                form_obj.total_absence = extra_leave
                form_obj.exatra_sort_leave = month_sort_leave
                form_obj.extra_late_present = late
                form_obj.save()
                messages.success(self.request, "Salary Updated Successfully")
            return super().form_valid(form)
        
        except Exception as e:
            print(e)
            return self.form_invalid(form)
            

    def form_invalid(self, form):
        messages.error(self.request, "Salary not updated please try again!")
        return super().form_invalid(form)

class DeleteCalculatedSalaryView(LoginRequiredMixin, AdminPassesTestMixin, DeleteView):
    model= MonthlySalary
    context_object_name ='salary'
    template_name = "authority/delete_calculated_salary.html"
    success_url = reverse_lazy('authority:calculated_salary_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Delete Calculated Salary" 
        return context

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save()
        return redirect(self.success_url)
    
    
     
    
    
     
        
    
    


