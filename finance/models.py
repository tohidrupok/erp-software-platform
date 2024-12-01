from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    account_type = models.CharField(
        max_length=50,
        choices=[('SR', 'SR'), ('Dealer', 'Dealer'), ('Admin', 'Admin'), ('HOS', 'HOS'), ('ROS', 'ROS'), ('Accounts', 'Accounts')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_type} - Balance: {self.balance}"

    def update_balance(self, amount):
        """Updates the account balance based on transaction amount."""
        self.balance += amount
        self.save()

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=50,
        choices=[('Credit', 'Credit'), ('Debit', 'Debit')]
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.transaction_date}"

    def save(self, *args, **kwargs):
        """Override save to update account balance when a transaction is made."""
        if self.transaction_type == 'Debit':
            self.account.update_balance(-self.amount)
        elif self.transaction_type == 'Credit':
            self.account.update_balance(self.amount)
        super().save(*args, **kwargs)


from django.db import models
from django.utils.timezone import now

class Source(models.Model): 
    name = models.CharField(max_length=255)  
    date = models.DateField(default=now) 
    note = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name
 

class Credit(models.Model):
    CREDIT_TYPE_CHOICES = [
        ('loan_bank', 'Loan from Bank'),
        ('own_investment', 'Own Investment'),
        ('order_price', 'Order\'s Total Price'),
    ]

    type = models.CharField(max_length=20, choices=CREDIT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=now)
    source = models.ForeignKey( 
        Source, 
        on_delete=models.CASCADE,  
        related_name='credits'  , blank=True, null=True
    )

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount}" 

class Debit(models.Model):
    DEBIT_TYPE_CHOICES = [
        ('cashout', 'Cashout'),
        ('office_cost', 'Office Management Cost'),
        ('factory_demand', 'Factory Demand Cash'),
    ]

    type = models.CharField(max_length=20, choices=DEBIT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=now)

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount}"

class TransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=now, blank=True, null=True )

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.amount}"

class FinanceSummary(models.Model):
    month = models.DateField()
    total_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_debit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    monthly_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def calculate_profit(self):
        self.monthly_profit = self.total_credit - self.total_debit
        self.save()

    def __str__(self):
        return f"Summary for {self.month.strftime('%B %Y')} - Profit: {self.monthly_profit}"
