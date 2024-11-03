
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Order

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pickup_location', 'drop_location', 'package_weight']
        widgets = {
            'pickup_location': forms.TextInput(attrs={'class': 'form-control'}),
            'drop_location': forms.TextInput(attrs={'class': 'form-control'}),
            'package_weight': forms.NumberInput(attrs={'class': 'form-control'}),
        }



#class LoginForm(forms.Form):
 #   username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
  #  password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
