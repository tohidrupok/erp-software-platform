from django import forms
from .models import Product, Order, Shop, DealerProductNeed


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = '__all__'


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['name', 'order_quantity']
        labels = {
            'name': 'পণ্য নির্বাচন করুন (অত্যাবশ্যক)', 
            'order_quantity': 'পণ্যের পরিমাণ নির্ধারণ করুন (অত্যাবশ্যক)' 
        }

class editOrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['name', 'order_quantity']


class DateSelectForm(forms.Form):
    date = forms.DateField(
        widget=forms.SelectDateWidget(),
        label="Select Date",
    )


class DealerProductNeedForm(forms.ModelForm):
    class Meta:
        model = DealerProductNeed
        fields = ['product', 'demand_quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class editdemandForm(forms.ModelForm):

    class Meta:
        model = DealerProductNeed
        fields = ['product', 'demand_quantity']

