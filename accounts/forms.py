from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, SellerProfile


class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Choose a strong password', 'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'city', 'area', 'pincode']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '10-digit mobile number', 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'e.g. Ahmedabad, Mumbai, Jaipur', 'class': 'form-control'}),
            'area': forms.TextInput(attrs={'placeholder': 'e.g. Navrangpura, Bandra West', 'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'placeholder': 'e.g. 380009', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        cpwd = cleaned_data.get('confirm_password')
        if pwd and cpwd and pwd != cpwd:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


class SellerRegistrationForm(CustomerRegistrationForm):
    business_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. Priya Homemade Pickles', 'class': 'form-control'}))
    whatsapp_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'WhatsApp number for orders', 'class': 'form-control'}), required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Tell customers about your products, specialties, and story...', 'rows': 3, 'class': 'form-control'}), required=False)

    class Meta(CustomerRegistrationForm.Meta):
        fields = CustomerRegistrationForm.Meta.fields + ['business_name', 'whatsapp_number', 'bio']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'city', 'area', 'pincode', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['business_name', 'bio', 'whatsapp_number', 'cover_image']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

