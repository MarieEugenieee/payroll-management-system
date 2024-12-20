from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

# Filters Class
from authority.filters import EmployeeListFilter

# class-based view classes
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

# Permission and Authentication
from django.contrib.auth.mixins import LoginRequiredMixin
from authority.permission import AdminPassesTestMixin

# Models Accounts
from accounts.models import User
from accounts.models import Profile
from accounts.models import PresentAddress
from accounts.models import PermanentAddress

# Models Employee
from employee.models import EmployeeInfo

# forms
from accounts.forms import EmployeeSignUpForm
from accounts.forms import ProfileForm
from accounts.forms import PresentAddressForm
from accounts.forms import PermanentAddressForm
from employee.forms import EmployeeInfoForm
from employee.forms import EmployeeSalaryForm


# View start from here
class AddEmployeeView(LoginRequiredMixin, AdminPassesTestMixin, CreateView):
    model = User
    form_class = EmployeeSignUpForm
    success_url = reverse_lazy('authority:authority')
    template_name = 'authority/add_employee.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Employee Accounts"
        return context

    def form_valid(self, form):
        if form.is_valid():
            user = form.save(commit=False)
            user.is_employee = True
            user.save()
            messages.success(self.request, "Employee Accounts Created Success Fully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "email or password invalid try aging")
        return super().form_invalid(form)


class EmployeeListView(LoginRequiredMixin, AdminPassesTestMixin, ListView):
    filterset_class = EmployeeListFilter
    template_name = 'authority/employee_list.html'
    context_object_name = 'employees'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Employee List"
        employee_filter = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        context["employees"] = employee_filter
        return context

    def get_queryset(self):
        # Filter to show only employees who are not archived and not staff
        return User.objects.filter(is_deleted=False, is_staff=False)


class EmployeeDetailView(LoginRequiredMixin, AdminPassesTestMixin, DetailView):
    queryset = User.objects.all()
    context_object_name = 'user'
    template_name = 'authority/employee_detail.html'

    def get_context_data(self, **kwargs):
        user_obj = User.objects.get(id=self.kwargs.get('pk'))
        context = super().get_context_data(**kwargs)
        context["title"] = "Employee Details"
        context["profile"] = Profile.objects.get(user=user_obj)
        context["employee_info"] = EmployeeInfo.objects.get(info_of=user_obj)
        context["present_address"] = PresentAddress.objects.get(address_of=user_obj)
        context["permanent_address"] = PermanentAddress.objects.get(address_of=user_obj)
        return context


class EditEmployeeView(LoginRequiredMixin, AdminPassesTestMixin, UpdateView):
    model = Profile
    model2 = EmployeeInfo
    form_class = ProfileForm
    form_class2 = EmployeeInfoForm
    template_name = 'authority/add_employee_info.html'
    success_url = reverse_lazy('authority:employee_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Employee Info"
        user_object = User.objects.get(id=self.kwargs.get('pk'))
        context["title"] = "Add Employee info"
        context["form"] = self.form_class(instance=user_object.profile)
        context["form2"] = self.form_class2(instance=user_object.employee_info)
        return context

    def post(self, request, *args, **kwargs):
        user_object = User.objects.get(id=self.kwargs.get('pk'))
        form = self.form_class(request.POST, request.FILES, instance=user_object.profile)
        form2 = self.form_class2(request.POST, request.FILES, instance=user_object.employee_info)
        return self.form_valid(form, form2)

    def form_valid(self, form, form2):
        try:
            if form.is_valid() and form2.is_valid():
                user = form.save(commit=False)
                info = form2.save(commit=False)
                user.profile = User.objects.get(id=self.kwargs.get('pk'))
                info.info_of = User.objects.get(id=self.kwargs.get('pk'))
                user.save()
                info.save()
                messages.success(self.request, "Employee Info Updated Successfully")
            return super().form_valid(form)

        except Exception as e:
            print(e)
            return super().form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Something went wrong, try again")
        return super().form_invalid(form)


class EditEmployeeAddressView(LoginRequiredMixin, AdminPassesTestMixin, UpdateView):
    model = PresentAddress
    model2 = PermanentAddress
    form_class = PresentAddressForm
    form_class2 = PermanentAddressForm
    template_name = 'authority/edit_address.html'
    success_url = reverse_lazy('authority:employee_list')

    def get_context_data(self, **kwargs):
        user_obj = User.objects.get(id=self.kwargs.get('pk'))
        context = super().get_context_data(**kwargs)
        context["title"] = "Add/Edit Address"
        context["present_address"] = self.form_class(instance=user_obj.present_address)
        context["permanent_address"] = self.form_class2(instance=user_obj.permanent_address)
        return context

    def post(self, request, *args, **kwargs):
        user_obj = User.objects.get(id=self.kwargs.get('pk'))
        form1 = self.form_class(request.POST, instance=user_obj.present_address)
        form2 = self.form_class2(request.POST, instance=user_obj.permanent_address)
        return self.form_valid(form1, form2)

    def form_valid(self, form, form2):
        if form.is_valid() and form2.is_valid():
            form.save()
            form2.save()
            messages.success(self.request, "Address Updated Successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Something went wrong, try again")
        return super().form_invalid(form)


class EditEmployeeSalaryView(LoginRequiredMixin, AdminPassesTestMixin, UpdateView):
    model = User
    form_class = EmployeeSalaryForm
    template_name = 'authority/edit_salary.html'
    success_url = reverse_lazy('authority:employee_list')

    def get_context_data(self, **kwargs):
        user_obj = User.objects.get(id=self.kwargs.get('pk'))
        employee_info_obj = EmployeeInfo.objects.get(info_of=user_obj)
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Salary"
        context["form"] = self.form_class(instance=employee_info_obj.salary_info)
        return context

    def post(self, request, *args, **kwargs):
        user_obj = User.objects.get(id=self.kwargs.get('pk'))
        employee_info_obj = EmployeeInfo.objects.get(info_of=user_obj)
        form = self.form_class(request.POST, instance=employee_info_obj.salary_info)
        return self.form_valid(form)

    def form_valid(self, form):
        if form.is_valid:
            form.save()
            messages.success(self.request, "Employee Salary Updated Successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Something went wrong, try again")
        return super().form_invalid(form)


class DeleteEmployeeView(LoginRequiredMixin, AdminPassesTestMixin, DeleteView):
    def post(self, request, pk, *args, **kwargs):
        # Get the employee object using pk, returns 404 if not found
        employee = get_object_or_404(User, pk=pk)

        # Permanently delete the employee
        employee.delete()

        # Add success message
        messages.success(request, "Employee deleted successfully.")

        # Redirect to the employee list
        return redirect('authority:employee_list')

    # Optionally, handle GET requests if you want to confirm deletion before posting
    def get(self, request, pk, *args, **kwargs):
        return self.post(request, pk, *args, **kwargs)

    def get_queryset(self):
        # Show only active employees (exclude deleted ones)
        return User.objects.all()