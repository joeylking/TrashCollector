from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import render
from django.apps import apps
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Employee
import calendar

# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.

@login_required
def index(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    Customer = apps.get_model('customers.Customer')
    logged_in_user = request.user

    try:
        today_date = date.today()
        today_day = calendar.day_name[today_date.weekday()]
        logged_in_employee = Employee.objects.get(user=logged_in_user)
        customers_in_zip = Customer.objects.filter(zip_code = logged_in_employee.zip_code)
        pickup_today = customers_in_zip.filter(weekly_pickup = today_day) | customers_in_zip.filter(one_time_pickup = today_date)
        non_suspended = pickup_today.exclude(suspend_start__lt = today_date, suspend_end__gt = today_date)
        customers_not_picked_up = non_suspended.exclude(date_of_last_pickup = today_date)
        
        context = {
            'logged_in_employee': logged_in_employee,
            'today_date': today_date,
            'today_day' : today_day,
            'customers_not_picked_up': customers_not_picked_up
        }
        return render(request, 'employees/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:create'))

@login_required
def create(request):
    logged_in_user = request.user
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip_code')
        new_employee = Employee(name=name_from_form, user=logged_in_user, zip_code=zip_from_form)
        new_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        return render(request, 'employees/create.html')

def edit_profile(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip_code')
        logged_in_employee.name = name_from_form
        logged_in_employee.zip_code = zip_from_form
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'logged_in_employee': logged_in_employee
        }
        return render(request, 'employees/edit_profile.html', context)

def serviced(request,customer_id):
    logged_in_user = request.user

    Customer = apps.get_model('customers.Customer')
    customer_info = Customer.objects.get(pk = customer_id)
    curr_date = date.today()
        
    if customer_info.date_of_last_pickup != curr_date:
        customer_info.date_of_last_pickup= curr_date
        customer_info.balance += 20
        customer_info.save()

    return HttpResponseRedirect(reverse('employees:index'))


def routes(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    Customer = apps.get_model('customers.Customer')
    customers = Customer.objects.filter(zip_code = logged_in_employee.zip_code)
    context = {
        'logged_in_employee':logged_in_employee,
        'customers' : customers
    }

    return render(request, 'employees/routes.html', context)

def daily(request, day):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    Customer = apps.get_model('customers.Customer')
    customers_in_zip = Customer.objects.filter(zip_code = logged_in_employee.zip_code)
    customers = customers_in_zip.filter(weekly_pickup = day)

    context = {
        'logged_in_employee':logged_in_employee,
        'customers' : customers,
        'day' : day
    }

    return render(request, 'employees/routes.html', context)