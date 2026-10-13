from django.db import models
import re
import bcrypt
from datetime import date

class UserManager(models.Manager):
    #register validation
    def reg_validation(self,data):
        errors={}

        firstname=data['firstname']
        lastname=data['lastname']
        email=data['email']
        password=data['password']
        confirm_pw=data['confirm_pw']

        if len(firstname) == 0:
            errors['firsnameerror']="firstname is required"
        if len(lastname) == 0:
            errors['lastnameerror']="lastname is required"
        if len(email) == 0:
            errors['emailerror']="email is required"
        if len(password) == 0:
            errors['passworderror']="password is required"
        if len(firstname) < 2:
            errors['firsnameerror']="firstname must be at least 2 chars"
        if len(lastname) < 2:
            errors['lastnameerror']="lastname must be at least 2 chars"
        if len(password) < 8:
            errors['passworderror']="password must be at least 8 chars"

        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

        if email and not EMAIL_REGEX.match(email):
            errors['emailerror']="email is invalid"

        if password != confirm_pw :
            errors['confirm_pwerror']="passwords do not match"

        if email and User.objects.filter(email=email).exists():
            errors['emailerror']="email already exists"

        return errors


    def create_user(self,data):
        firstname=data['firstname']
        lastname=data['lastname']
        email=data['email']
        password=data['password']
        

        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user=User.objects.create(firstname=firstname,lastname=lastname,email=email,password=pw_hash)

        return user

    def login_validation(self,data):
        errors={}

        email=data['email']
        password=data['password']

        if len(email) == 0:
            errors['loginemailerror']="email is required"
        if len(password) == 0:
            errors['loginpassworderror']="password is required"

        if len(errors) == 0 :
            user = User.objects.filter(email=email)
            if user :
                logged_user=user[0]

                if not bcrypt.checkpw(password.encode(), logged_user.password.encode()):
                   errors['loginerror']="invalid email or paswword"
            #when user does not exist
            else:
                errors['loginerror']="invalid email or paswword"

        return errors

    def login_user(self,data):

        email=data['email']
        password=data['password']
        user=User.objects.get(email=email)
        if bcrypt.checkpw(password.encode(), user.password.encode()):
            return user
        return None

class shipmentManager(models.Manager):
    #shipment validation
    def shipment_validation(self,data):
        errors={}

        name=data['name']
        number=data['number']
        status=data['status']
        eta=data['eta']
        vessel=data['vessel']
        origin=data['origin']
        destination=data['destination']
        lastchecked=data['lastchecked']

        if len(name) == 0:
            errors['nameerror']="name is required"
        if len(number) == 0:
            errors['numbererror']="number is required"
        elif len(name) > 5:
            errors['nameerror']="name must be at least 4 characters"
        elif len(number) != 11:
            errors['numbererror']="number must be 11 characters"
        if not re.fullmatch(r'[A-Z]{4}[0-9]{7}',number):
            errors['numbererror']="Invalid container number format"

        return errors

    def create_shipment(self,data,user):
        name=data['name']
        number=data['number']
        
        shipment=Shipment.objects.create(name=name,number=number,user=user)

        return shipment

    def update_shipment(self,data,shipment):
        shipment.name=data['name']
        shipment.number=data['number']
        shipment.save()

    
class User(models.Model):
    firstname=models.CharField(max_length=255)
    lastname=models.CharField(max_length=255)
    email=models.CharField(max_length=255)
    password=models.CharField(max_length=255)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    objects=UserManager()

class Shipment(models.Model):
    name=models.CharField(max_length=100)
    number=models.CharField(max_length=20,unique=True)
    status=models.CharField(max_length=100,default="Unknown")
    eta=models.DateTimeField(null=True,blank=True)
    vessel=models.CharField(max_length=150,blank=True)
    origin=models.CharField(max_length=150,blank=True)
    destination=models.CharField(max_length=150,blank=True)
    lastchecked=models.DateTimeField(null=True,blank=True)
    user=models.ForeignKey(User,related_name="shipments",on_delete=models.DO_NOTHING)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    objects=shipmentManager()

class shipmentHistory(models.Model):
    shipment=models.ForeignKey(Shipment,related_name='history',on_delete=models.CASCADE)
    status=models.CharField(max_length=100)
    location=models.CharField(max_length=150,blank=True)
    eta=models.DateTimeField(null=True,blank=True)
    created_at=models.DateField(auto_now_add=True)