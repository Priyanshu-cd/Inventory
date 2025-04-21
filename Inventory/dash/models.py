from django.db import models
from django.utils import timezone


# ---------------------------------
# 1. Organization Model
# ---------------------------------
class Organization(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Ideally, use Django's auth system

    def __str__(self):
        return self.name

# ---------------------------------
# 2. Project Model (under Organization)
# ---------------------------------
class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                      related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    advance_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    lifetime_advance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    buy_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sell_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profit_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} ({self.organization.name})"



# ---------------------------------
# 4. Inventory Model (under Transaction)
# ---------------------------------
class Inventory(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                      related_name='inventories')
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_buy= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_sell = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.product_name} - Qty: {self.quantity}"

# ---------------------------------
# 5. Advance Detail Model (under Transaction)
# ---------------------------------
class AdvanceDetail(models.Model):
    MODE_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                      related_name='advance_details')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Advance of {self.amount} ({self.mode})"

