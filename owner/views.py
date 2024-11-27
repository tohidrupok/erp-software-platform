from django.shortcuts import render, redirect
from dashboard.models import *
from django.contrib.auth.decorators import login_required
from dashboard.decorators import auth_users, allowed_users
from dashboard.forms import ProductForm
from django.contrib import messages

#offer

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from dashboard.models import Offer
from .forms import OfferForm

def home(request):
    customer = User.objects.filter()
    customer_count = customer.count()
    product = Product.objects.all()
    product_count = product.count()
    order = Order.objects.all()
    order_count = order.count()


    is_admin = request.user.groups.filter(name='Admin').exists()
    context = {
        'customer': customer,
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
         'is_admin': is_admin
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
            form.save()
            product_name = form.cleaned_data.get('name')
            messages.success(request, f'{product_name} has been added')
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




 

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse

from django.contrib import messages
@login_required(login_url='user-login')
@allowed_users(allowed_roles=['Admin'])
def delivery_done(request, need_id): 
    # Get the DealerProductNeed object
    need = get_object_or_404(DealerProductNeed, id=need_id)
    
    # Check if the product exists
    if not need.product:
        messages.error(request, "Product does not exist.")
        return redirect('dealers_demand') 
    
    # Check if stock is sufficient
    if need.product.stock_quantity is None:
        messages.error(request, "Product stock is not defined.")
        return redirect('dealers_demand') 
    
    if need.product.stock_quantity < need.demand_quantity:
        messages.error(request, "Insufficient stock to fulfill the demand.")
        return redirect('dealers_demand') 
    
    # Deduct stock and update status 
    if need.status == 'HOS_Approve':
        need.product.stock_quantity -= need.demand_quantity
        need.product.save()
        need.status = "Admin_Approve"  
        need.admin_flag= True
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
