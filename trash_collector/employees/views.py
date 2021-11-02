from django.http import HttpResponse, HttpResponseRedirect
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
        non_suspended = pickup_today.filter(today_date < pickup_today.suspend_start) |  pickup_today.filter(today_date > pickup_today.suspend_end)
        
        
        context = {
            'logged_in_employee': logged_in_employee,
            'today_date': today_date,
            'today_day' : today_day,
            'non_suspended': non_suspended
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
        customer_info.save()

    update_balance(customer_id)

    return HttpResponseRedirect(reverse('employees:route'))


def update_balance(customer_id):
    Customer = apps.get_model('customers.Customer')
    customer_being_confirmed = Customer.objects.get(pk = customer_id)
    customer_being_confirmed.balance += 20
    customer_being_confirmed.save()