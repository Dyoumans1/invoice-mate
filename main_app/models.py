from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField()
    email = models.EmailField()
    address = models.CharField()
    phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
# class Invoice(models.Model):
#     STATUS_CHOICES = [
#         ('paid', 'Paid'),
#         ('pending', 'Pending'),
#         ('overdue', 'Overdue'),
#     ]
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
#     invoice_number = models.CharField(max_length=50)
#     issue_date = models.DateField()
#     due_date = models.DateField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
#     notes = models.TextField(blank=True)
#     subtotal = models.DecimalField()
#     tax_rate = models.DecimalField()
#     tax_amount = models.DecimalField()
#     total_amount = models.DecimalField()
#     created_at = models.DateField(default=timezone.now)

#     def _str_(self):

# class Item(models.Model):
#     invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
#     description = 
#     quantity = m
#     unit_price = 
#     total_price = 
#     created_at = 
    
#     def __str__(self):
#         return self.description