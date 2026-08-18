import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, SellerProfile


def validate_phone(phone_str):
    if not phone_str:
        return phone_str
    phone_clean = phone_str.strip()
    # Strip leading +91 or + if user pasted +919876543210
    phone_digits = re.sub(r'^\+?(?:91)?', '', phone_clean)
    if not phone_digits.isdigit() or len(phone_digits) != 10:
        raise forms.ValidationError("Please enter a valid 10-digit mobile number containing digits only.")
    return phone_digits


def validate_pincode(pincode_str):
    if not pincode_str:
        return pincode_str
    pincode_clean = pincode_str.strip()
    if not pincode_clean.isdigit() or len(pincode_clean) != 6:
        raise forms.ValidationError("Please enter a valid 6-digit PIN code (digits only).")
    return pincode_clean


def validate_password_strength(password):
    if len(password) < 8:
        raise forms.ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise forms.ValidationError("Password must contain at least one uppercase letter (A-Z).")
    if not re.search(r'[a-z]', password):
        raise forms.ValidationError("Password must contain at least one lowercase letter (a-z).")
    if not re.search(r'[0-9]', password):
        raise forms.ValidationError("Password must contain at least one digit (0-9).")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', password):
        raise forms.ValidationError("Password must contain at least one special character (e.g. @$!%*#?&).")
    return password


class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'e.g. Pass@123',
        'class': 'form-control',
        'required': 'required'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password',
        'class': 'form-control',
        'required': 'required'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'city', 'area', 'pincode']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'e.g. priya_sharma', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'e.g. priya@example.com', 'class': 'form-control', 'required': 'required'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'e.g. 9876543210 (10 digits)',
                'class': 'form-control',
                'type': 'tel',
                'pattern': '[0-9]{10}',
                'maxlength': '10',
                'inputmode': 'numeric',
                'required': 'required',
                'title': 'Please enter a 10-digit mobile number (e.g. 9876543210)'
            }),
            'city': forms.TextInput(attrs={'placeholder': 'e.g. Ahmedabad, Mumbai, Jaipur', 'class': 'form-control'}),
            'area': forms.TextInput(attrs={'placeholder': 'e.g. Navrangpura, Bandra West', 'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={
                'placeholder': 'e.g. 380009 (6 digits)',
                'class': 'form-control',
                'pattern': '[0-9]{6}',
                'maxlength': '6',
                'inputmode': 'numeric',
                'required': 'required',
                'title': 'Please enter a 6-digit PIN code (e.g. 380009)'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError("Email address is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address is already registered.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        return validate_phone(phone)

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode', '').strip()
        if not pincode:
            raise forms.ValidationError("Pincode is required.")
        return validate_pincode(pincode)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return validate_password_strength(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        cpwd = cleaned_data.get('confirm_password')
        if pwd and cpwd and pwd != cpwd:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


class SellerRegistrationForm(CustomerRegistrationForm):
    business_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. Priya Homemade Pickles', 'class': 'form-control'}))
    whatsapp_number = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'e.g. 9876543210 (10 digits)',
        'class': 'form-control',
        'type': 'tel',
        'pattern': '[0-9]{10}',
        'maxlength': '10',
        'inputmode': 'numeric',
        'title': 'Please enter a 10-digit WhatsApp number (e.g. 9876543210)'
    }), required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Tell customers about your products, specialties, and story...', 'rows': 3, 'class': 'form-control'}), required=False)

    class Meta(CustomerRegistrationForm.Meta):
        fields = CustomerRegistrationForm.Meta.fields + ['business_name', 'whatsapp_number', 'bio']

    def clean_whatsapp_number(self):
        whatsapp = self.cleaned_data.get('whatsapp_number', '').strip()
        if whatsapp:
            return validate_phone(whatsapp)
        return whatsapp


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'city', 'area', 'pincode', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. user@example.com'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'pattern': '[0-9]{10}',
                'maxlength': '10',
                'inputmode': 'numeric',
                'placeholder': 'e.g. 9876543210',
                'title': 'Please enter a 10-digit mobile number (e.g. 9876543210)'
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]{6}',
                'maxlength': '6',
                'inputmode': 'numeric',
                'placeholder': 'e.g. 380009',
                'title': 'Please enter a 6-digit PIN code (e.g. 380009)'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("An account with this email address is already registered.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone:
            return validate_phone(phone)
        return phone

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode', '').strip()
        if pincode:
            return validate_pincode(pincode)
        return pincode


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['business_name', 'bio', 'whatsapp_number', 'cover_image']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'pattern': '[0-9]{10}',
                'maxlength': '10',
                'inputmode': 'numeric',
                'placeholder': 'e.g. 9876543210',
                'title': 'Please enter a 10-digit WhatsApp number (e.g. 9876543210)'
            }),
        }

    def clean_whatsapp_number(self):
        whatsapp = self.cleaned_data.get('whatsapp_number', '').strip()
        if whatsapp:
            return validate_phone(whatsapp)
        return whatsapp

