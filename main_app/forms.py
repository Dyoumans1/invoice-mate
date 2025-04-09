from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Item, Invoice, Client

class CustomUserCreationForm(UserCreationForm):
    company = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'company']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.company = self.cleaned_data['company']
            user.save()

        return user
    

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'address', 'phone', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'invoice_number', 'issue_date', 'due_date', 'status', 'notes', 'tax_rate']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'})
        }