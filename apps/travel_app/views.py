from django.shortcuts import render, redirect
from IPython import embed
from django.contrib import messages

from .models import User
from .models import Trip

def index(request):
  return render(request, "travel_app/index.html")

def register(request):
  user_hash = {
    "first_name" : request.POST['first_name'],
    "last_name" : request.POST['last_name'],
    "email" : request.POST['email'],
    "password" : request.POST['password'],
    "password_confirmation" : request.POST['password_confirmation']
  }
  user = User.objects.register(user_hash)
  # user = User.objects.register(request.POST) 
  if user[0] == True:
    request.session['user_id'] = user[1].id
    messages.success(request, request.POST['email'] + ' successfully created')
    return redirect("/travels")
  else:  
    # user[1] is an array of errors
    for m in user[1]:
      messages.error(request, m)

  return redirect("/")

def login(request):
  user_hash = {
    "email" : request.POST['email'],
    "password" : request.POST['password']
  }
  user = User.objects.login(user_hash)
  if user[0] == True:
    request.session['user_id'] = user[1].id
    messages.success(request, request.POST['email'] + ' successfully logged in')
    return redirect("/travels")
  else:  
    # user[1] is an array of errors
    for m in user[1]:
      messages.error(request, m)
    return redirect("/")

def logout(request):
  request.session.clear()
  return redirect("/")    

def travels(request):
  if 'user_id' not in request.session:
    return redirect("/")
  else: 
    user = User.objects.get(id=request.session['user_id'])
    context = {
      "user" : user,
      "your_trips" : user.joined_trips.all(),
      #user.wishlisted_items.all(),
      "others_trips" : Trip.objects.exclude(joined_by=user),
      #Item.objects.exclude(wishlisted_by=user)
    }
    return render(request, "travel_app/travels.html", context)

def travels_join(request):
  trip = Trip.objects.get(id=request.POST['travel_id'])
  user = User.objects.get(id=request.session['user_id'])
  trip.joined_by.add(user)
  return redirect("/travels")   

def destination(request,id):
  context = {
      "trip" : Trip.objects.get(id=id)
    }
  return render(request, "travel_app/destination.html", context)

def travels_create(request):
  travel_hash = {
    'destination' : request.POST['destination'],
    'description' : request.POST['description'],
    'date_from' : request.POST['date_from'],
    'date_to' : request.POST['date_to'],
    'created_by' : User.objects.get(id=request.session['user_id'])
  }
  travel_dict = Trip.objects.create_with_validations(travel_hash)

  if not travel_dict['is_valid']:
    for e in travel_dict['errors']:
      messages.error(request, e)
    return redirect("/travels/new")
  else:      
    return redirect("/travels")

def travels_new(request):
  return render(request, "travel_app/travels_new.html")