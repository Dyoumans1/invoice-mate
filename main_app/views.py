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