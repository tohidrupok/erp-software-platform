from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 

class Zone(models.Model):
    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    thana = models.CharField(max_length=100)
    area = models.CharField(max_length=100)

    def __str__(self):
        return f"Zone: {self.name}, District: {self.district}, Thana: {self.thana}, Area: {self.area}"

class Shop(models.Model):
    shop_name = models.CharField(max_length=200, verbose_name="Shop Name")
    shop_owner = models.CharField(max_length=200, verbose_name="Shop Owner")
    shop_phone = models.CharField(max_length=15, verbose_name="Shop Phone")
    shop_nid = models.CharField(max_length=20, verbose_name="Shop NID")
    shop_email = models.EmailField(max_length=254, verbose_name="Shop Email")
    shop_address = models.TextField(verbose_name="Shop Address")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name="Shop Zone")

    def __str__(self):
        return self.shop_name 
    


class Department(models.Model):
    name = models.CharField(max_length=200, verbose_name="Department/Company Name")

    def __str__(self):
        return self.name

class Product(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Dept/Company")
    
    name = models.CharField(max_length=200, verbose_name="Product Name")
    product_code = models.CharField(max_length=100, unique=True, verbose_name="Product Code")
    product_dp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Product DP")  
    product_tp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Product TP")  
    product_mrp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Product MRP")  
    product_sku = models.CharField(max_length=100, unique=True, verbose_name="Product SKU")  
    product_factor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Product Factor")
    product_details = models.TextField(verbose_name="Product Details", blank=True, null=True) 
    stock_quantity = models.PositiveIntegerField(null=True, blank= True)


    def update_stock(self, quantity):
        """Updates the stock quantity of the product."""
        self.stock_quantity += quantity
        self.save()


    def __str__(self):
        return f"{self.name} - {self.product_code}"

    def discounted_price(self, timestamp):
        """
        This method calculates the product's discounted price based on active offers at the given timestamp.
        If there is no active offer at the timestamp, it returns the original TP (trade price).
        """
        active_offer = self.get_active_offer_at(timestamp)  # Get the active offer at the order's creation time
        if active_offer:
            discount = (self.product_tp * active_offer.discount_percentage) / 100
            return self.product_tp - discount
        return self.product_tp
    
    def discount(self, timestamp):
        """
        This method calculates the product's discounted price based on active offers at the given timestamp.
        If there is no active offer at the timestamp, it returns the original TP (trade price).
        """
        active_offer = self.get_active_offer_at(timestamp)  # Get the active offer at the order's creation time
        if active_offer:
            discount = (self.product_tp * active_offer.discount_percentage) / 100
            return discount
        return 0

    def get_active_offer_at(self, timestamp):
        """Returns the active offer for this product at the specified timestamp."""
        return self.offers.filter(start_date__lte=timestamp, end_date__gte=timestamp).first()

class Offer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def update_discount(self, new_discount):


        self.discount_percentage = new_discount
        self.save()

    def end_offer(self):
        self.end_date = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.discount_percentage}% off on {self.product.name}" 
    
   
CATEGORY = (
    ('Pending', 'Pending'),
    ('Delivered', 'Delivered'),
    ('Stock Unavailable', 'Stock Unavailable'),
    ('On the Way', 'On the Way'),
)

class Order(models.Model):
    name = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, verbose_name="Select Item Name ")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order_quantity = models.PositiveIntegerField(null=True, verbose_name="Item Quantity")
    status = models.CharField(max_length=20, choices=CATEGORY, default='Pending')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name="Shop" )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created", blank=True, null=True)
    
    def __str__(self):
        return f'{self.customer}-{self.name}'

    def net_amount(self):
        """Calculates the total price before discount for the order."""
        if self.name is None:
            return 0
        return self.order_quantity * self.name.product_tp

    def gross_amount(self):
        """Calculates the total price after applying the discount."""
        if self.name is None:
            return 0
        return self.order_quantity * self.name.discounted_price(self.created_at) 
    
    def discount_amount(self):
        """Calculates the total price after applying the discount."""
        if self.name is None:
            return 0
        return self.order_quantity * self.name.discount(self.created_at) 
    
    

class FinalOrder(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Customer", blank= True, null= True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name="Shop", blank= True, null= True)
    orders = models.ManyToManyField(Order, verbose_name="Select Orders")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")

    def __str__(self):
        return f'Order ID: {self.id} -Shop: {self.shop} - SR: {self.customer}' 

    def net_amount(self):
        total_net = 0
        for order in self.orders.all():
            if order.name:
                total_net += order.order_quantity * order.name.product_tp
        return total_net

    def gross_amount(self):
        total_gross = 0
        for order in self.orders.all():
            if order.name:
                total_gross += order.order_quantity * order.name.discounted_price()
        return total_gross



CATEGORY = (
    ('Pending', 'Pending'),
    ('ROS_Approve', 'ROS_Approve'),
    ('HOS_Approve', 'HOS_Approve'),
    ('Admin_Approve', 'Admin_Approve'),
    ('Delivered_by_factory', 'Delivered_by_factory'),  
    ('Received', 'Received'),  

)

DemandStatus = (
    ('Pending', 'Pending'),
    ('Done', 'Done'),
)

class DealerProductNeed(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Select Item")
    demand_quantity = models.PositiveIntegerField(null=True, verbose_name="Item Quantity")
    dealer = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=CATEGORY, default='Pending')  
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    rsm_flag = models.BooleanField(default=False) 
    hos_flag = models.BooleanField(default=False) 
    admin_flag = models.BooleanField(default=False) 
    dealer_flag = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.product} - {self.status} for {self.dealer}" 
    
    def net_amount(self):
        if self.product is None:
            return 0
        return self.demand_quantity * self.product.product_dp
    
    def gross_amount(self):
        if self.product is None:
            return 0
        return self.demand_quantity * self.product.product_dp
    
  
class DealerOrder(models.Model):
    dealer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    status = models.CharField(max_length=20, choices=DemandStatus, default='Pending') 
    products = models.ManyToManyField(DealerProductNeed, verbose_name="Select Orders") 

    def __str__(self):
        return f"{self.products} - {self.status} for {self.dealer}" 


    

class Stock(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Customer")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"Stock for {self.customer.username if self.customer else 'No Customer'}"

class StockItem(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="stock_items", verbose_name="Stock")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    available_stock = models.PositiveIntegerField(default=0, verbose_name="Available Stock")
    reserved_stock = models.PositiveIntegerField(default=0, verbose_name="Reserved Stock")  # Reserved for orders
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    def __str__(self):
        return f"{self.product.name} - {self.available_stock} available"

    def add_stock(self, quantity):
        """Add stock for this product."""
        if quantity > 0:
            self.available_stock += quantity
            self.save()

    def remove_stock(self, quantity):
        """Remove stock for this product."""
        if quantity > 0 and self.available_stock >= quantity:
            self.available_stock -= quantity
            self.save()

    def reserve_stock(self, quantity):
        """Reserve stock for an order."""
        if quantity > 0 and self.available_stock >= quantity:
            self.available_stock -= quantity
            self.reserved_stock += quantity
            self.save()

    def release_reserved_stock(self, quantity):
        """Release reserved stock if an order is canceled."""
        if quantity > 0 and self.reserved_stock >= quantity:
            self.available_stock += quantity
            self.reserved_stock -= quantity
            self.save()
