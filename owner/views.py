from django.shortcuts import render, redirect
from dashboard.models import *
from django.contrib.auth.decorators import login_required
from dashboard.decorators import auth_users, allowed_users
from dashboard.forms import ProductForm
from django.contrib import messages

#offer#offer#offer#offer

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from dashboard.models import Offer
from .forms import OfferForm
from datetime import date

def home(request):
    customer = User.objects.filter()
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()

    dealer_demand = DealerOrder.objects.filter(created_at__date=date.today()).order_by('-created_at')
    now = timezone.now()
    active_offers = Offer.objects.filter(start_date__lte=now, end_date__gte=now)

    for final_order in dealer_demand:
        filtered_orders = final_order.products.all().order_by('-created_at')
        final_order.filtered_orders = filtered_orders

        # Calculate the totals for the filtered orders
        total_quantity = sum(order.demand_quantity for order in filtered_orders)
        total_amount = sum(order.product.product_dp for order in filtered_orders)
        total_net_amount = sum(order.demand_quantity * order.product.product_dp for order in filtered_orders)
        total_gross_amount = sum(order.demand_quantity * order.product.product_dp for order in filtered_orders)

        # Attach the totals to the final_order object for use in the template
        final_order.total_quantity = total_quantity
        final_order.total_amount = total_amount
        final_order.total_net_amount = total_net_amount
        final_order.total_gross_amount = total_gross_amount

    
    is_admin = request.user.groups.filter(name='Admin').exists()
    context = {
        'customer': customer,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'is_admin': is_admin,
        'offers': active_offers,
        'final_orders': dealer_demand,
        
    } 
    return render(request, 'home.html', context) 


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def customers(request):
    # Get today's date
    today = timezone.now().date()
    
    active_customers = User.objects.filter(last_login__date=today)
    inactive_customers = User.objects.filter(last_login__date__lt=today)
    
    customer_count = User.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    
    is_admin = request.user.groups.filter(name='Admin').exists()
    
    context = {
        'active_customers': active_customers,
        'inactive_customers': inactive_customers,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'is_admin': is_admin
    }
    
    return render(request, 'dashboard/customers.html', context)

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def customer_detail(request, pk):
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()
    customers = User.objects.get(id=pk)
    context = {
        'customers': customers,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,

    }
    return render(request, 'dashboard/customers_detail.html', context)

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def order(request):
    order = Order.objects.all()
    order_count = order.count()
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    
    is_admin = request.user.groups.filter(name='Admin').exists()
    context = {
        'order': order,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
         'is_admin': is_admin
    }
    return render(request, 'dashboard/order.html', context) 

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def products(request):
    product = Product.objects.all()
    product_count = product.count()
    customer = User.objects.filter(groups=2)
    customer_count = customer.count()
    order = Order.objects.all()
    order_count = order.count()
    product_quantity = Product.objects.filter(name='')
    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            # Save the new product
            product = form.save()

            # Get the stock quantity from the form
            stock_quantity = form.cleaned_data.get('stock_quantity')

            # Get or create the stock for the current user
            stock, _ = Stock.objects.get_or_create(customer=request.user)

            StockItem.objects.create(
                stock=stock,
                product=product,
                available_stock=stock_quantity, 
                reserved_stock=0,               
            )

            # Success message
            messages.success(request, f'{product.name} has been added with {stock_quantity} units in stock.')
            return redirect('dashboard-products')
    else:
        form = ProductForm()
    
    for p in product:
        p.active_offer = p.get_active_offer_at(timezone.now()) 
        

    is_admin = request.user.groups.filter(name='Admin').exists()
    context = {
        'product': product,
        'form': form,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'is_admin': is_admin
    }
    return render(request, 'dashboard/products.html', context)



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def product_edit(request, pk):
    item = Product.objects.get(id=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard-products')
    else:
        form = ProductForm(instance=item)
    
    is_admin = request.user.groups.filter(name='Admin').exists()
    context = {
        'form': form,
        'is_admin': is_admin
    }
    return render(request, 'dashboard/products_edit.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def product_delete(request, pk):
    item = Product.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('dashboard-products')
    
    is_admin = request.user.groups.filter(name='Admin').exists()
    context = {
        'item': item,
         'is_admin': is_admin
    }
    
    return render(request, 'dashboard/products_delete.html', context) 


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def final_order_list(request):
    
    # Get all FinalOrder objects
    final_orders = FinalOrder.objects.all().order_by('-created_at')

    for final_order in final_orders:
        filtered_orders = final_order.orders.all().order_by('-created_at')
        final_order.filtered_orders = filtered_orders

        # Calculate the totals for the filtered orders
        total_quantity = sum(order.order_quantity for order in filtered_orders)
        total_net_amount = sum(order.order_quantity * order.name.product_tp for order in filtered_orders)
        total_gross_amount = sum(order.order_quantity * order.name.discounted_price(order.created_at) for order in filtered_orders)
        total_discount_amount = sum(order.order_quantity * order.name.discount(order.created_at) for order in filtered_orders)

        # Attach the totals to the final_order object for use in the template
        final_order.total_quantity = total_quantity
        final_order.total_net_amount = total_net_amount
        final_order.total_gross_amount = total_gross_amount
        final_order.total_discount_amount = total_discount_amount

        


    # Pass the final orders to the template
    is_admin = request.user.groups.filter(name='Admin').exists()
    context = {
        'final_orders': final_orders,
        'is_admin': is_admin
    }
    
    return render(request, 'dashboard/admin_all_orders.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def dealers_demand(request):
   
    # Get all FinalOrder objects
    dealer_demand = DealerOrder.objects.all().order_by('-created_at')

    for final_order in dealer_demand:
        filtered_orders = final_order.products.all().order_by('-created_at')
        final_order.filtered_orders = filtered_orders

        # Calculate the totals for the filtered orders
        total_quantity = sum(order.demand_quantity for order in filtered_orders)
        total_amount = sum(order.product.product_dp for order in filtered_orders)
        total_net_amount = sum(order.demand_quantity * order.product.product_dp for order in filtered_orders)
        total_gross_amount = sum(order.demand_quantity * order.product.product_dp for order in filtered_orders)

        # Attach the totals to the final_order object for use in the template
        final_order.total_quantity = total_quantity
        final_order.total_amount = total_amount
        final_order.total_net_amount = total_net_amount
        final_order.total_gross_amount = total_gross_amount

    # Pass the final orders to the template
    is_admin = request.user.groups.filter(name='Admin').exists()
    context = {
        'final_orders': dealer_demand,
        'is_admin': is_admin
    }
    
    return render(request, 'admin/all_dealer_demand.html', context)   



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def delivery_done(request, need_id): 
    need = get_object_or_404(DealerProductNeed, id=need_id)
    
    if not need.product:
        messages.error(request, "Product does not exist.")
        return redirect('dealers_demand') 

    stock, _ = Stock.objects.get_or_create(customer=request.user)
    stock_item = StockItem.objects.filter(stock=stock, product=need.product).first()

    if not stock_item:
        messages.error(request, "Stock item for this product does not exist.")
        return redirect('dealers_demand') 

    if stock_item.available_stock < need.demand_quantity:
        messages.error(request, "Insufficient stock to fulfill the demand.")
        return redirect('dealers_demand') 

    if need.status == 'HOS_Approve':
        stock_item.available_stock -= need.demand_quantity  
        stock_item.save()

        need.status = "Admin_Approve"
        need.admin_flag = True
        need.save()
        
        messages.success(request, "Delivery marked as complete and stock updated.")
    
    return redirect('dealers_demand')



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def offer_list(request):
    now = timezone.now()
    active = Offer.objects.filter(start_date__lte=now, end_date__gte=now).order_by('-created_at')
    inactive = Offer.objects.filter(start_date__gt=now) | Offer.objects.filter(end_date__lt=now)
    inactive = inactive.order_by('-created_at')
    is_admin = request.user.groups.filter(name='Admin').exists()
    return render(request, 'admin/offer_list.html', {'active': active,'inactive': inactive, 'is_admin': is_admin })


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def offer_create(request):
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('offer_list')
    else:
        form = OfferForm()
    is_admin = request.user.groups.filter(name='Admin').exists()
    return render(request, 'admin/offer_form.html', {'form': form, 'is_admin': is_admin })

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def offer_update(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('offer_list')
    else:
        form = OfferForm(instance=offer)
    is_admin = request.user.groups.filter(name='Admin').exists()
    return render(request, 'admin/offer_form.html', {'form': form,'is_admin': is_admin})

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def offer_end(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.end_offer()
    return redirect('offer_list')

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def offer_delete(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    offer.delete()
    return redirect('offer_list') 

#stock management


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def admin_stocks(request):

    stocks = Stock.objects.filter(customer=request.user).prefetch_related('stock_items')

    is_admin = request.user.groups.filter(name='Admin').exists() 
    
    context = {
        'stocks': stocks,
        'is_admin': is_admin,
    }
    return render(request, 'admin/admin_stocks.html', context)  


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def manage_stock_view(request):
    if request.method == 'POST':
        stock_item_id = request.POST.get("stock_item_id")
        action = request.POST.get("action")
        quantity = request.POST.get("quantity", "0")

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be a positive integer.")
        except ValueError:
            messages.error(request, "Invalid quantity.")
            return admin_stocks(request)

        stock = Stock.objects.filter(customer=request.user).first()
        if not stock:
            messages.error(request, "Stock not found.")
            return admin_stocks(request)

        stock_item = get_object_or_404(stock.stock_items, id=stock_item_id)

        # Perform the requested action
        if action == "add":
            stock_item.available_stock += quantity
            stock_item.count_stock += quantity
            messages.success(request, f"{quantity} units added to {stock_item.product.name}.")
            
        elif action == "remove":
            if stock_item.available_stock >= quantity:
                stock_item.available_stock -= quantity
                stock_item.count_stock -= quantity
                messages.success(request, f"{quantity} units removed from {stock_item.product.name}.")
            else:
                messages.error(request, "Insufficient stock to remove.")
            
        elif action == "reserve":
            if stock_item.available_stock >= quantity:
                stock_item.available_stock -= quantity
                stock_item.reserved_stock += quantity
                messages.success(request, f"{quantity} units reserved from {stock_item.product.name}.")
            else:
                messages.error(request, "Insufficient stock to reserve.")
        elif action == "release":
            if stock_item.reserved_stock >= quantity:
                stock_item.reserved_stock -= quantity
                stock_item.available_stock += quantity
                messages.success(request, f"{quantity} units released to available stock for {stock_item.product.name}.")
            else:
                messages.error(request, "Insufficient reserved stock to release.")
        else:
            messages.error(request, "Invalid action specified.")

        # Save the changes
        stock_item.save()

    return admin_stocks(request)