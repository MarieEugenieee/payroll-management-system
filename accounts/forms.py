from django import forms
from django.contrib.auth.forms import UserCreationForm

# models
from accounts.models import User
from accounts.models import Profile
from accounts.models import PresentAddress
from accounts.models import PermanentAddress
from django.contrib.auth import get_user_model


# Widgets
from accounts.widgets import CustomPictureImageFieldWidget



User = get_user_model()

class ChangePasswordForm(forms.Form):
    email = forms.EmailField(required=True, label="Email")
    old_password = forms.CharField(widget=forms.PasswordInput, required=True, label="Old Password")
    new_password = forms.CharField(widget=forms.PasswordInput, required=True, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")
        
        return cleaned_data

# forms
DEPARTMENT_OPT = (
    ('HR', 'Human Resource'),
    ('administrative', 'Administrative'),
    ('software development', 'Software Development'),
    ('QA', 'Quality Assurance'),
    ('project management', 'Project Management'),
    ('Product Management', 'Product Management'),
    ('design', 'Design'),
    ('devOps', 'DevOps'),
    ('customer support', 'Customer Support'),
    ('marketing', 'Marketing'),
    ('IT', 'Information Technology')
)
GENDER_OPT = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
)

class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2',)

class EmployeeSignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2','is_employee','is_staff')

class ProfileForm(forms.ModelForm):
    photo = forms.ImageField(widget=CustomPictureImageFieldWidget)

    class Meta:
        model = Profile
        exclude = ('user',)


class PresentAddressForm(forms.ModelForm):

    class Meta:
        model = PresentAddress
        exclude = ('address_of',)


class PermanentAddressForm(forms.ModelForm):

    class Meta:
        model = PermanentAddress
        exclude = ('address_of',)
