from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Client, Invoice, Item
from .forms import CustomUserCreationForm
from .forms import ItemForm

class Home(LoginView):
    template_name = 'home.html'

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('client-index')
        else:
            error_message = 'Invalid sign up - try again'
    form = CustomUserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

def about(request):
    return render(request, 'about.html')

@login_required
def dashboard(request):
    invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')[:5]
    clients = Client.objects.filter(user=request.user).order_by('-id')[:5]
    return render(request, 'main_app/dashboard.html', {'invoices': invoices,'clients': clients })


def client_index(request):
    clients = Client.objects.filter(user=request.user)
    return render(request, 'clients/index.html', {'clients': clients})


def client_detail(request, client_id):
    client = Client.objects.get(Client, id=client_id, user=request.user)
    return render(request, 'clients/detail.html', {
        'client': client,
    })

class ClientCreate(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['name', 'email', 'address', 'phone', 'notes']
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ClientUpdate(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ['name', 'email', 'address', 'phone', 'notes']

class ClientDelete(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = '/clients/'

class ClientList(LoginRequiredMixin, ListView):
    model = Client
    
    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)
    
@login_required
def invoice_index(request):
    invoices = Invoice.objects.filter(user=request.user)
    return render(request, 'invoices/index.html', {'invoices': invoices})

@login_required
def invoice_detail(request, invoice_id):
    invoice = Invoice.objects.get(Invoice, id=invoice_id, user=request.user)
    item_form = ItemForm()
    return render(request, 'invoices/detail.html', {
        'invoice': invoice, 
        'item_form': item_form
    })    
    
class InvoiceCreate(LoginRequiredMixin, CreateView):
    model = Invoice
    fields = ['client', 'invoice_number', 'issue_date', 'due_date', 'notes', 'subtotal', 'tax_rate']
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.tax_amount = form.instance.subtotal * (form.instance.tax_rate / 100)
        form.instance.total_amount = form.instance.subtotal + form.instance.tax_amount
        return super().form_valid(form)

class InvoiceUpdate(LoginRequiredMixin, UpdateView):
    model = Invoice
    fields = ['client', 'invoice_number', 'issue_date', 'due_date', 'status', 'notes', 'tax_rate']

class InvoiceDelete(LoginRequiredMixin, DeleteView):
    model = Invoice
    success_url = '/invoices/'

class ItemCreate(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    
    def form_valid(self, form):
        form.instance.invoice_id = self.kwargs.get('invoice_id')
        form.instance.user = self.request.user
        form.instance.total_price = form.instance.quantity * form.instance.unit_price
        
        response = super().form_valid(form)
        
        invoice = form.instance.invoice
        invoice.subtotal += form.instance.total_price
        invoice.tax_amount = invoice.subtotal * (invoice.tax_rate / 100)
        invoice.total_amount = invoice.subtotal + invoice.tax_amount
        invoice.save()
        
        return response
    
    def get_success_url(self):
        return f'/invoices/{self.kwargs.get("invoice_id")}/'


class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = Item
    fields = ['description', 'quantity', 'unit_price']
    
    def form_valid(self, form):
        original_total = self.object.total_price
        form.instance.total_price = form.instance.quantity * form.instance.unit_price
        
        invoice = self.object.invoice
        invoice.subtotal = invoice.subtotal - original_total + form.instance.total_price
        invoice.tax_amount = invoice.subtotal * (invoice.tax_rate / 100)
        invoice.total_amount = invoice.subtotal + invoice.tax_amount
        invoice.save()
        
        return super().form_valid(form)

class ItemDelete(LoginRequiredMixin, DeleteView):
    model = Item
    
    def get_success_url(self):
        invoice_id = self.object.invoice.id
        
        invoice = self.object.invoice
        invoice.subtotal -= self.object.total_price
        invoice.tax_amount = invoice.subtotal * (invoice.tax_rate / 100)
        invoice.total_amount = invoice.subtotal + invoice.tax_amount
        invoice.save()
        return f'/invoices/{invoice_id}/'