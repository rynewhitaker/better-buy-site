from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from shop.models.defaults.order import Order
from betterbuysite.models import Product

# Create your views here.
def index(request):
    template = loader.get_template("DroneDelivery/index.html")
    queryset = {
        'drone_orders': Order.objects.all(),
        'items' : Product.objects.all(),
    }
    return render(request, 'DroneDelivery/index.html', queryset)