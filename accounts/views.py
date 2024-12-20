from django.shortcuts import HttpResponse, redirect, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, FormView
from django.contrib.messages.views import SuccessMessageMixin
from accounts.models import User
from accounts.forms import SignUpForm, ChangePasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm


# Signup View
class SignupView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('accounts:logout')
    template_name = 'accounts/signup.html'


# Login View
class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Login Page"
        return context

    def form_valid(self, form):
        username = self.request.POST['username']
        password = self.request.POST['password']

        try:
            request_user = User.objects.get(email=username)
            user = authenticate(self.request, username=username, password=password)

            if user is not None and request_user.is_superuser and request_user.is_staff:
                login(self.request, user)
                return HttpResponseRedirect(reverse('authority:authority'))
                
            elif user is not None and request_user.is_employee:
                login(self.request, user)
                return HttpResponseRedirect(reverse('employee:employee'))

            elif user is not None and request_user.is_employee and request_user.is_staff:
                login(self.request, user)
                return HttpResponseRedirect(reverse('authority:authority'))

            elif user is not None and request_user.is_employee and request_user.is_receptonist:
                login(self.request, user)
                return HttpResponseRedirect(reverse('reception:reception_home'))

           

            else:
                if User.objects.filter(email=username).exists() and not request_user.is_active:
                    messages.warning(self.request, f"{username}, this email doesn't have login permission")
                return HttpResponseRedirect(reverse('accounts:login'))

        except Exception as e:
            print(e)
            messages.error(self.request, "Invalid credentials.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid User email or password")
        return super().form_invalid(form)


# Logout View
class UserLogout(LoginRequiredMixin, LogoutView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('accounts:login'))


# Change Password View with Email and Old Password
class UserPasswordChangeView(SuccessMessageMixin, FormView):
    template_name = 'accounts/change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('accounts:login')
    success_message = "Password changed successfully."

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        old_password = form.cleaned_data.get('old_password')
        new_password = form.cleaned_data.get('new_password')
        
        try:
            user = User.objects.get(email=email)
            
            # Verify the old password
            if not user.check_password(old_password):
                messages.error(self.request, "Old password is incorrect.")
                return self.form_invalid(form)
            
            # Set the new password
            user.set_password(new_password)
            user.save()

            # Re-authenticate the user if they are changing their own password
            if self.request.user.is_authenticated and self.request.user.email == email:
                update_session_auth_hash(self.request, user)
            
            messages.success(self.request, "Password updated successfully!")
        except User.DoesNotExist:
            messages.error(self.request, "User with this email does not exist.")
            return self.form_invalid(form)
        
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
