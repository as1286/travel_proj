from __future__ import unicode_literals
from IPython import embed
from django.db import models
import re
import bcrypt
import datetime
from dateutil.parser import parse as parse_date

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.
class UserManager(models.Manager):
  def register(self, postData):
    errors = []
    if len(User.objects.filter(email=postData['email'])) > 0:
      errors.append("Email Address already taken!")

    if len(postData['first_name']) < 2:
      errors.append("First Name cannot be empty!")
    if len(postData['last_name']) < 2:
      errors.append("Last Name cannot be empty!")
    if len(postData['email']) < 1:
      errors.append("Email cannot be empty!")
    elif not EMAIL_REGEX.match(postData['email']):
      errors.append("Invalid Email Address!")

    if len(postData['password']) < 1:
      errors.append("Password cannot be empty!")
    elif len(postData['password']) <= 8:
      errors.append("Password must be greater than 8 characters!") 
    if len(postData['password_confirmation']) < 1:
      errors.append("Password confirmation cannot be empty!")      
    elif postData['password'] != postData['password_confirmation']:
      errors.append("Password must match password confirmation")       

    if has_numbers(postData['first_name']):
      errors.append("First Name cannot contain numbers")
    if has_numbers(postData['last_name']):
      errors.append("Last Name cannot contain numbers")  

    if len(errors) == 0:
      hashed_pw = bcrypt.hashpw(postData['password'].encode('utf-8'), bcrypt.gensalt()) 
      u = User.objects.create(first_name = postData['first_name'], last_name = postData['last_name'], email = postData['email'], password = hashed_pw)
      return (True, u)
    else:
      return (False, errors)

  def login(self, postData):
    errors = []
    u = User.objects.filter(email=postData['email'])
    if len(u) == 0:
      errors.append("Invalid Email/Password")
    else:
      stored_hash = u[0].password
      input_hash = bcrypt.hashpw(postData['password'].encode(), stored_hash.encode())
      if not input_hash == stored_hash:
        errors.append("Invalid Email/Password")

    if len(errors) == 0:
      return (True, u[0])
    else:
      return (False, errors)

def has_numbers(inputString):
  return any(char.isdigit() for char in inputString)

# u1 = User.objects.create(first_name="shane", last_name="chang", email="sc@example.com")
class User(models.Model):
  first_name = models.CharField(max_length=38)
  last_name = models.CharField(max_length=38)
  email = models.CharField(max_length=38)
  password = models.CharField(max_length=38)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  objects = UserManager()
  
  def __unicode__(self):
    return "id: " + str(self.id) + ", email: " + self.email

class TripManager(models.Manager):
  def create_with_validations(self, object_hash):
    errors = []

    if len(object_hash['description']) < 1:
      errors.append("description must not be blank")
    if len(object_hash['destination']) < 1:
      errors.append("destination must not be blank") 

    date_from = parse_date(object_hash['date_from'])
    date_to = parse_date(object_hash['date_to'])

    if date_from < datetime.datetime.today():
      errors.append("date_from must be future dated") 
    if date_from > date_to:
      errors.append("date_from cannot be after date_to") 

    if len(errors) == 0:
      trip = Trip.objects.create(description=object_hash['description'], destination=object_hash['destination'], created_by=object_hash['created_by'], date_from=object_hash['date_from'], date_to=object_hash['date_to'])
      trip.joined_by.add(object_hash['created_by'])

      object_dict = {
        'is_valid': True,
        'trip' : trip
      }
      return object_dict
    else:
      object_dict = {
        'is_valid': False,
        'errors' : errors
      }
      return object_dict

    
class Trip(models.Model):
  description = models.CharField(max_length=38)
  destination = models.CharField(max_length=38)
  date_from = models.DateField()
  date_to = models.DateField()
  created_by = models.ForeignKey(User, related_name="created_trips") 
  created_at = models.DateTimeField(auto_now_add=True)
  joined_by = models.ManyToManyField(User, related_name="joined_trips")
  objects = TripManager()

  def __unicode__(self):
    return "id: " + str(self.id) + ", description: " + self.description
