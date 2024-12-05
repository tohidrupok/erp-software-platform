from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Product, Order, Zone, Shop , FinalOrder, DealerProductNeed, DealerOrder ,Offer, Stock , StockItem
from .forms import ProductForm, OrderForm , ShopForm , DateSelectForm , DealerProductNeedForm , editOrderForm, editdemandForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import auth_users, allowed_users

from django.http import JsonResponse
from django.utils import timezone
from django.forms import formset_factory
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.db import transaction

from django.core.paginator import Paginator
from django.utils import timezone 
from django.urls import reverse

@login_required(login_url='user-login')
def base(request):
    is_sr = request.user.groups.filter(name='SR').exists()
    is_dealer = request.user.groups.filter(name='DEALER').exists()
    is_rsm = request.user.groups.filter(name='RSM').exists()
    is_hos = request.user.groups.filter(name='HOS').exists() 
    is_finance = request.user.groups.filter(name='Finance').exists() 
    print(is_finance)
    context = {
        'is_sr': is_sr,
        'is_dealer': is_dealer,
        'is_rsm': is_rsm,
        'is_hos': is_hos,
        'is_finance': is_finance,

    }
    return render(request, 'dashboard/base.html', context)



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR']) 

def index(request):
    today = timezone.now().date()  
    selected_date = request.GET.get('selected_date', today) 
    zones = Zone.objects.values('name').distinct()
    shops = None
    selected_shop = None
    shop_orders = None

    ProductOrderFormset = formset_factory(OrderForm, extra=1)

    # Retrieve zone, district, thana, and area from session if available
    selected_zone_name = request.session.get('selected_zone_name')
    selected_zone_district = request.session.get('selected_zone_district')
    selected_zone_thana = request.session.get('selected_zone_thana')
    selected_zone_area = request.session.get('selected_zone_area')

    if request.method == 'GET':
        zone_name = request.GET.get('zone_name')
        zone_district = request.GET.get('zone_district')
        zone_thana = request.GET.get('zone_thana')
        zone_area = request.GET.get('zone_area')

        if zone_name:
            # Store these selections in session to retain them after redirect
            request.session['selected_zone_name'] = zone_name
            request.session['selected_zone_district'] = zone_district
            request.session['selected_zone_thana'] = zone_thana
            request.session['selected_zone_area'] = zone_area
            
            # Filter the zones based on the selections
            filtered_zones = Zone.objects.filter(
                name=zone_name,
                district=zone_district,
                thana=zone_thana,
                area=zone_area
            )
            shops = Shop.objects.filter(zone__in=filtered_zones)

        # Retrieve selected shop from session if available
        if 'selected_shop_id' in request.session:
            try:
                selected_shop = Shop.objects.get(id=request.session['selected_shop_id'])
                shop_orders = Order.objects.filter(shop=selected_shop, customer=request.user, created_at__date=selected_date).order_by('-created_at')
            except Shop.DoesNotExist:
                selected_shop = None
                shop_orders = None

    if request.method == 'POST':
        formset = ProductOrderFormset(request.POST)
        selected_shop_id = request.POST.get('selected_shop')

        if selected_shop_id:
            try:
                selected_shop = Shop.objects.get(id=selected_shop_id)
                request.session['selected_shop_id'] = selected_shop_id  # Store in session
            except Shop.DoesNotExist:
                selected_shop = None

        if formset.is_valid() and selected_shop:
            with transaction.atomic():  
                final_order = FinalOrder.objects.create(
                    customer=request.user,
                    shop=selected_shop
                )

                for form in formset:
                    obj = form.save(commit=False)
                    obj.customer = request.user
                    obj.shop = selected_shop
                    obj.save()  

                    final_order.orders.add(obj)

                final_order.save()

            # Redirect after processing the formset with session variables carried over
            return redirect(f'{reverse("dashboard-index")}?zone_name={selected_zone_name}&zone_district={selected_zone_district}&zone_thana={selected_zone_thana}&zone_area={selected_zone_area}')

    else:
        formset = ProductOrderFormset()

    is_sr = request.user.groups.filter(name='SR').exists()

    # Calculate totals after checking for shop orders
    total_net_amount = total_gross_amount = total_quantity = total_discount_amount = 0
    if shop_orders:
        for order in shop_orders:
            total_net_amount += order.net_amount()
            total_gross_amount += order.gross_amount()
            total_discount_amount += order.discount_amount()
            total_quantity += order.order_quantity

    context = {
        'is_sr': is_sr,
        'formset': formset,
        'zones': zones,
        'shops': shops,
        'selected_shop': selected_shop,
        'shop_orders': shop_orders,
        'total_net_amount': total_net_amount,
        'total_gross_amount': total_gross_amount,
        'total_discount_amount': total_discount_amount,
        'total_quantity': total_quantity,
        'selected_date': selected_date,  
        'today': today,
        'selected_zone_name': selected_zone_name,
        'selected_zone_district': selected_zone_district,
        'selected_zone_thana': selected_zone_thana,
        'selected_zone_area': selected_zone_area,
    }

    return render(request, 'dashboard/index.html', context)

# def index(request):
#     today = timezone.now().date()  # Get today's date (timezone-aware)
#     selected_date = request.GET.get('selected_date', today) 
#     zones = Zone.objects.values('name').distinct()
#     shops = None
#     selected_shop = None
#     shop_orders = None

#     ProductOrderFormset = formset_factory(OrderForm, extra=1)

#     if request.method == 'GET':

#         zone_name = request.GET.get('zone_name')
#         zone_district = request.GET.get('zone_district')
#         zone_thana = request.GET.get('zone_thana')
#         zone_area = request.GET.get('zone_area')

#         if zone_name:
#             filtered_zones = Zone.objects.filter(
#                 name=zone_name,
#                 district=zone_district,
#                 thana=zone_thana,
#                 area=zone_area
#             )
#             shops = Shop.objects.filter(zone__in=filtered_zones)

#         # Retrieve selected shop from session if available
#         if 'selected_shop_id' in request.session:
#             try:
#                 selected_shop = Shop.objects.get(id=request.session['selected_shop_id'])
#                 shop_orders = Order.objects.filter(shop=selected_shop, customer=request.user, created_at__date=selected_date).order_by('-created_at')
#             except Shop.DoesNotExist:
#                 selected_shop = None
#                 shop_orders = None

#     if request.method == 'POST':
#         formset = ProductOrderFormset(request.POST)
#         selected_shop_id = request.POST.get('selected_shop')

#         if selected_shop_id:
#             try:
#                 selected_shop = Shop.objects.get(id=selected_shop_id)
#                 request.session['selected_shop_id'] = selected_shop_id  # Store in session
#             except Shop.DoesNotExist:
#                 selected_shop = None

#         if formset.is_valid() and selected_shop:
#             with transaction.atomic():  
#                 # final_order, created = FinalOrder.objects.get_or_create(
#                 #     customer=request.user,
#                 #     shop=selected_shop
#                 # )
#                 final_order = FinalOrder.objects.create(
#                         customer=request.user,
#                         shop=selected_shop
#                     )

#                 # Iterate over each form in the formset to create Order objects
#                 for form in formset:
#                     obj = form.save(commit=False)
#                     obj.customer = request.user
#                     obj.shop = selected_shop
#                     obj.save()  

#                     # Add each Order to the FinalOrder
#                     final_order.orders.add(obj)

#                 # trigger any additional save logic
#                 final_order.save()

#             # Redirect after processing the formset
#             return redirect('dashboard-index')

#     else:
#         formset = ProductOrderFormset()

#     is_sr = request.user.groups.filter(name='SR').exists()

#     # Calculate totals after checking for shop orders
#     total_net_amount = total_gross_amount = total_quantity = total_discount_amount = 0
#     if shop_orders:
#         for order in shop_orders:
#             total_net_amount += order.net_amount()
#             total_gross_amount += order.gross_amount()
#             total_discount_amount += order.discount_amount()
#             total_quantity += order.order_quantity

#     context = {
#         'is_sr':is_sr,
#         'formset': formset,
#         'zones': zones,
#         'shops': shops,
#         'selected_shop': selected_shop,
#         'shop_orders': shop_orders,
#         'total_net_amount': total_net_amount,
#         'total_gross_amount': total_gross_amount,
#         'total_discount_amount': total_discount_amount,
#         'total_quantity': total_quantity,
#         'selected_date': selected_date,  
#         'today': today  
#     }

#     return render(request, 'dashboard/index.html', context)


def get_districts(request):
    zone_name = request.GET.get('zone_name')
    if zone_name:
        districts = Zone.objects.filter(name=zone_name).values_list('district', flat=True).distinct()
        return JsonResponse({'districts': list(districts)})
    return JsonResponse({'districts': []})

def get_thanas(request):
    district_name = request.GET.get('district_name')
    if district_name:
        thanas = Zone.objects.filter(district=district_name).values_list('thana', flat=True).distinct()
        return JsonResponse({'thanas': list(thanas)})
    return JsonResponse({'thanas': []})

def get_areas(request):
    thana_name = request.GET.get('thana_name')
    if thana_name:
        areas = Zone.objects.filter(thana=thana_name).values_list('area', flat=True).distinct()
        return JsonResponse({'areas': list(areas)})
    return JsonResponse({'areas': []})



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])

def shops(request):
    shops = Shop.objects.all()
    shop_count = shops.count()

    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            form.save()
            shop_name = form.cleaned_data.get('shop_name')
            messages.success(request, f'{shop_name} has been added')
            return redirect('add-shope')
    else:
        form = ShopForm()
    
    is_sr = request.user.groups.filter(name='SR').exists()
    context = {
        'shops': shops,
        'form': form,       
        'shop_count': shop_count,  
        'is_sr': is_sr,     
    }
         
    return render(request, 'dashboard/add_shop.html', context) 


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def daily_report(request):
    today = timezone.now()
    start_date = None
    end_date = None

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        
        if not start_date and end_date:
            start_date = end_date

        
        if not end_date and start_date:
            end_date = start_date
        
        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

            date_range = (min(start_date, end_date), max(start_date, end_date))
            orders_today = Order.objects.filter(created_at__date__range=date_range, customer=request.user)
        else:
            orders_today = Order.objects.none()  
    else:
        orders_today = Order.objects.filter(created_at__date=today.date(), customer=request.user)

    total_quantity = sum(order.order_quantity for order in orders_today)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    context = {
        'orders_today': orders_today,
        'total_quantity': total_quantity,
        'today': today,
        'start_date': start_date,
        'end_date': end_date,
        'is_sr': is_sr,
    }
    
    return render(request, 'dashboard/daily_report.html', context)

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER','SR'])
def active_offer_list(request):
    now = timezone.now()
    active_offers = Offer.objects.filter(start_date__lte=now, end_date__gte=now)

    is_sr = request.user.groups.filter(name='SR').exists()
    is_dealer = request.user.groups.filter(name='DEALER').exists()
    return render(request, 'dashboard/active_offer_list.html', {'offers': active_offers,'is_sr': is_sr,'is_dealer': is_dealer}) 


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['SR'])
def order_manage(request):
    now = timezone.now()    
    orders = FinalOrder.objects.filter(customer=request.user).order_by('-created_at')

    paginator = Paginator(orders, 15)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
       

    for final_order in page_obj:
        filtered_orders = final_order.orders.filter(customer=request.user).order_by('-created_at')
        final_order.filtered_orders = filtered_orders

        total_quantity = sum(order.order_quantity for order in filtered_orders)
        total_net_amount = sum(order.order_quantity * order.name.product_tp for order in filtered_orders)
        total_gross_amount = sum(order.order_quantity * order.name.discounted_price(order.created_at) for order in filtered_orders)
        total_discount_amount = sum(order.order_quantity * order.name.discount(order.created_at) for order in filtered_orders)

        final_order.total_quantity = total_quantity
        final_order.total_net_amount = total_net_amount
        final_order.total_gross_amount = total_gross_amount
        final_order.total_discount_amount = total_discount_amount

 
    is_sr = request.user.groups.filter(name='SR').exists()

    return render(request, 'dashboard/order_manage.html', {'page_obj': page_obj, 'is_sr': is_sr})



def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = editOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated successfully!")
            return redirect('edit_order', pk=order.pk)
    else:
        form = editOrderForm(instance=order)
    
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/edit_order.html', {'form': form, 'order': order, 'is_sr': is_sr})


def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, "Order deleted successfully!")
        return redirect('order_manage')  
    is_sr = request.user.groups.filter(name='SR').exists()
    return render(request, 'dashboard/confirm_delete_order.html', {'order': order,'is_sr': is_sr})








#######Dealer#########################Dealer Start ############################# Dealer Start #######################Dealer Start ########################Dealer Start ####################
from .models import Order, Product, Shop, Zone
from user.models import Profile

def get_orders_for_dealer_by_product_and_zone(dealer_zones, dealer_products):

    matching_orders = FinalOrder.objects.filter(
        orders__shop__zone__in=dealer_zones ,
        orders__name__in=dealer_products 
         
    ).distinct().order_by('-created_at')
    return matching_orders

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER'])
def dealer_orders_view(request):
    user = request.user  
    dealer_profile = Profile.objects.get(customer=user)  

    dealer_zones = dealer_profile.zones.all()  
    dealer_products = dealer_profile.products.all()  

    final_orders = get_orders_for_dealer_by_product_and_zone(dealer_zones, dealer_products)

    for final_order in final_orders:
        filtered_orders = final_order.orders.filter(name__in=dealer_products).order_by('-created_at')
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


    is_dealer = request.user.groups.filter(name='DEALER').exists()

    context = {
        'final_orders': final_orders,
        'is_dealer': is_dealer,
    }
 
    return render(request, 'dashboard/dealer_sr_order_view.html', context)


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER'])
def demand(request):
    ProductDemandFormset = formset_factory(DealerProductNeedForm, extra=1)  

    if request.method == 'POST':
        formset = ProductDemandFormset(request.POST)

        if formset.is_valid():
            with transaction.atomic():
             
                dealer_order = DealerOrder(dealer=request.user)
                dealer_order.save()
             
                for form in formset:
                    product_need = form.save(commit=False)
                    product_need.dealer = request.user 
                    product_need.status = 'Pending'
                    product_need.save() 
               
                    dealer_order.products.add(product_need)

                dealer_order.save()
        
            return redirect('demand_check')

    is_dealer = request.user.groups.filter(name='DEALER').exists()
    formset = ProductDemandFormset()  

    context = {
        'formset': formset,
        'is_dealer': is_dealer,
    }

    return render(request, 'dashboard/dealer_requesr_demand.html', context) 



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER'])
def edit_demand(request, pk):
    order = get_object_or_404(DealerProductNeed, pk=pk)
    if request.method == 'POST':
        form = editdemandForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Demand updated successfully!")
            return redirect('demand_check')
    else:
        form = editdemandForm(instance=order)
    
    is_dealer = request.user.groups.filter(name='DEALER').exists()
    return render(request, 'dashboard/edit_order.html', {'form': form, 'order': order, 'is_dealer': is_dealer})



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER'])
def delete_demand(request, pk):
    demand = get_object_or_404(DealerProductNeed, pk=pk)
    if request.method == 'POST':
        demand.delete()
        messages.success(request, "Demand deleted successfully!")
        return redirect('demand_check')  
    is_dealer = request.user.groups.filter(name='DEALER').exists()
    return render(request, 'dashboard/confirm_delete_order.html', {'order': demand,'is_dealer': is_dealer}) 



@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER'])
def demand_request_check(request):

    user = request.user
    
    dealer_demand = DealerOrder.objects.filter(dealer= user).order_by('-created_at')

    for final_order in dealer_demand:
        filtered_orders = final_order.products.all()
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

    is_dealer = request.user.groups.filter(name='DEALER').exists()
    context = {
        'final_orders': dealer_demand,
        'is_dealer': is_dealer,
    }
    
    return render(request, 'dashboard/dealer_demand_check.html', context)   


@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER'])
def user_stocks(request):

    stocks = Stock.objects.filter(customer=request.user).prefetch_related('stock_items')

    is_dealer = request.user.groups.filter(name='DEALER').exists()
    context = {
        'stocks': stocks,
        'is_dealer': is_dealer,
    }
    return render(request, 'dashboard/dealer_stocks.html', context)


from finance.models import Account , Credit , TransactionHistory
from django.utils.timezone import now

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER'])
def reached_product(request, need_id):
    # Get the DealerProductNeed object
    need = get_object_or_404(DealerProductNeed, id=need_id)

    # Ensure the product exists
    if not need.product:
        messages.error(request, "The specified product does not exist.")
        return redirect('demand_check')

    # Ensure the logged-in user has an associated stock
    stock, created = Stock.objects.get_or_create(customer=request.user)

    # Find or create the stock item for the product
    stock_item, created = StockItem.objects.get_or_create(
        stock=stock,
        product=need.product,
        defaults={"available_stock": 0, "reserved_stock": 0}
    )
   
   
    # Update the need's status
    if need.status == 'Admin_Approve':
        stock_item.add_stock(need.demand_quantity)
        need.status = "Received"
        need.dealer_flag= True

        delear_account, created = Account.objects.get_or_create(user=request.user)
        delear_account.update_balance(need.gross_amount())
        
        stock_item.save()

        Credit.objects.create(
            type='order_price',
            amount=need.gross_amount(),
            description=f"Dealer {request.user}, Demand price for product:  [{need.product.product_code}, {need.product.name}]",
            date=now()
        ) 

        TransactionHistory.objects.create( 
            transaction_type='credit',
            details = 'order_price',
            amount=need.gross_amount(),
            description=f"Dealer {request.user}, Demand price for Product Code: [{need.product.product_code}], Product Name: [{need.product.name}]",
            date=now()
            
        ) 
        messages.success(request, "Product received successfully and stock updated.")

    need.save()
 
    return redirect('demand_check')   

@login_required(login_url='user-login')
@allowed_users(allowed_roles=['DEALER'])

def dealer_approved(request, need_id): 
    need = get_object_or_404(Order, id=need_id)
        
    if need.status != 'Delivered':               
        need.status = "Delivered"
        need.save()        
        messages.success(request, "Successfully delivered to the shop through the SR.")
    
    return redirect('sr-order') 