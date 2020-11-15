from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def index(request):
    context = {}
    template = loader.get_template("DroneDelivery/index.html")
    return render(request, 'DroneDelivery/index.html')