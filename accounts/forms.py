from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User


class RegisterForm(forms.Form):
    ROLES = [('tourist','Tourist'),('vehicle_owner','Vehicle Owner'),
             ('hotel_owner','Hotel Owner'),('guide','Tour Guide')]
    first_name       = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
    last_name        = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
    username         = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    email            = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email Address'}))
    phone            = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Phone (optional)'}))
    role             = forms.ChoiceField(choices=ROLES, widget=forms.Select(attrs={'class':'form-select'}))
    password         = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is taken.')
        return username

    def clean(self):
        cd = super().clean()
        if cd.get('password') != cd.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')
        return cd


class LoginForm(forms.Form):
    email    = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name','last_name','phone','bio','address','city','state','profile_picture']
        widgets = {f: forms.TextInput(attrs={'class':'form-control'}) for f in ['first_name','last_name','phone','city','state']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].widget     = forms.Textarea(attrs={'class':'form-control','rows':3})
        self.fields['address'].widget = forms.Textarea(attrs={'class':'form-control','rows':2})


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter your registered email'})
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No account found with this email address.')
        return email


class ResetPasswordForm(forms.Form):
    password         = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'New Password', 'id': 'new_pw'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Confirm New Password'})
    )

    def clean(self):
        cd = super().clean()
        if cd.get('password') != cd.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')
        return cd
