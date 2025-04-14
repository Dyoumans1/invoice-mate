from django.http import HttpResponse
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
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.conf import settings
import tempfile
import os

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
    client = Client.objects.get(id=client_id, user=request.user)
    return render(request, 'clients/detail.html', {'client': client})

class ClientCreate(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['name', 'email', 'address', 'phone', 'notes']
    template_name = 'clients/client_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ClientUpdate(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ['name', 'email', 'address', 'phone', 'notes']
    template_name = 'clients/client_form.html'

class ClientDelete(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = '/clients/'
    template_name = 'clients/client_confirm_delete.html'

class ClientList(LoginRequiredMixin, ListView):
    model = Client

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)
    

# had help with formset.is_valid and calculations

@login_required
def invoice_index(request):
    invoices = Invoice.objects.filter(user=request.user)
    return render(request, 'invoices/index.html', {'invoices': invoices})

@login_required
def invoice_detail(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id, user=request.user)
    item_form = ItemForm()
    return render(request, 'invoices/detail.html', {'invoice': invoice, 'item_form': item_form})

class InvoiceCreate(LoginRequiredMixin, CreateView):
    model = Invoice
    fields = ['client', 'invoice_number', 'issue_date', 'due_date', 'notes', 'tax_rate']
    template_name = 'invoices/invoice_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ItemFormSet = inlineformset_factory(Invoice, Item, fields=('description', 'quantity', 'unit_price'), extra=1, can_delete=False)
        
        if self.request.POST:
            context['item_formset'] = ItemFormSet(self.request.POST, instance=self.object)
        else:
            context['item_formset'] = ItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.subtotal = 0
        response = super().form_valid(form)
        
        ItemFormSet = inlineformset_factory(Invoice, Item, fields=('description', 'quantity', 'unit_price'), extra=1)
        formset = ItemFormSet(self.request.POST, instance=self.object)
        
        if formset.is_valid():
            subtotal = 0
            for item in formset.save(commit=False):
                item.user = self.request.user
                item.total_price = item.quantity * item.unit_price
                item.save()
                subtotal += item.total_price
            
            self.object.subtotal = subtotal
            self.object.tax_amount = subtotal * (self.object.tax_rate / 100)
            self.object.total_amount = self.object.subtotal + self.object.tax_amount
            self.object.save()
        
        return response

class InvoiceUpdate(LoginRequiredMixin, UpdateView):
    model = Invoice
    fields = ['client', 'invoice_number', 'issue_date', 'due_date', 'status', 'notes', 'tax_rate']
    template_name = 'invoices/invoice_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ItemFormSet = inlineformset_factory(Invoice, Item, fields=('description', 'quantity', 'unit_price'), extra=1)
        context['item_formset'] = ItemFormSet(self.request.POST or None, instance=self.object)
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        ItemFormSet = inlineformset_factory(Invoice, Item, 
                                            fields=('description', 'quantity', 'unit_price'), 
                                            extra=1,
                                            can_delete=True)
        formset = ItemFormSet(self.request.POST, instance=self.object)

        if formset.is_valid():
            subtotal = 0
            
            for item_form in formset.forms:
                if not item_form.cleaned_data:
                    continue
                    
                if item_form.cleaned_data.get('DELETE', False):
                    if item_form.instance.pk:
                        item_form.instance.delete()
                else:
                    item = item_form.save(commit=False)
                    item.user = self.request.user
                    item.total_price = item.quantity * item.unit_price
                    item.save()
                    subtotal += item.total_price
            
            self.object.subtotal = subtotal
            self.object.tax_amount = subtotal * (self.object.tax_rate / 100)
            self.object.total_amount = self.object.subtotal + self.object.tax_amount
            self.object.save()

        return response
    

# followed instructions to add weasyprint
def generate_pdf_invoice(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id, user=request.user)

    context = {
        'invoice': invoice,
        'request': request,
    }
    
    html_string = render_to_string('invoices/pdf_invoice.html', context)
    
    from django.contrib.staticfiles import finders
    css_path = finders.find('css/pdf.css')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output:
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        css = CSS(filename=css_path)
        
        pdf_file = html.write_pdf(stylesheets=[css])
        
        output.write(pdf_file)
    
    with open(output.name, 'rb') as f:
        pdf_content = f.read()
   
    os.unlink(output.name)
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    
    return response

class InvoiceDelete(LoginRequiredMixin, DeleteView):
    model = Invoice
    success_url = '/invoices/'
    template_name = 'invoices/invoice_confirm_delete.html'

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