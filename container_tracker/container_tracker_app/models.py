from django.db import models
import re
import bcrypt
from datetime import date
import requests
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import json
import os
from django.core.mail import send_mail
from django.conf import settings


#retrieve the data from Traqo.
def fetch_container_data(number):

    api_key = os.environ.get("TRAQO_API_KEY")

    if not api_key:
        print("Traqo API key is missing")
        return None

    url = f"https://traqocontainer.com/api/v1/container/{number}"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=60
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print("Traqo API error:", error)
        return None

    result = response.json()

    if result.get("success"):
        return result.get("data")

    return None

#handles Traqo's date format
def parse_api_datetime(value):
    if not value:
        return None

    parsed = parse_datetime(value.replace(" ", "T", 1))

    if parsed and timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)

    return parsed


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
            errors['firstnameerror']="firstname is required"
        if len(lastname) == 0:
            errors['lastnameerror']="lastname is required"
        if len(email) == 0:
            errors['emailerror']="email is required"
        if len(password) == 0:
            errors['passworderror']="password is required"
        if len(firstname) < 2:
            errors['firstnameerror']="firstname must be at least 2 chars"
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


    def login_user(self, data):
        errors = self.login_validation(data)

        if len(errors) == 0:
            email = data['email']
            user = User.objects.get(email=email)
            return user

        return None

class shipmentManager(models.Manager):
    #shipment validation
    def shipment_validation(self,data):
        errors={}

        name=data['name']
        number=data['number']
        # status=data['status']
        # eta=data['eta']
        # vessel=data['vessel']
        # origin=data['origin']
        # destination=data['destination']
        # lastchecked=data['lastchecked']

        if len(name) == 0:
            errors['nameerror']="name is required"
        if len(number) == 0:
            errors['numbererror']="number is required"
        elif len(name) < 5:
            errors['nameerror']="name must be at least 4 characters"
        elif len(number) != 11:
            errors['numbererror']="number must be 11 characters"
        if not re.fullmatch(r'[A-Z]{4}[0-9]{7}',number):
            errors['numbererror']="Invalid container number format"

        return errors

    
    
    def save_tracking_data(self, shipment, api_data):

        # 1. Save the OLD values before updating the shipment
        old_status = shipment.status
        old_eta = shipment.eta
        old_ata = shipment.ata
        was_checked = shipment.lastchecked is not None

        # 2. Update the current shipment information
        shipment.status = api_data.get("status") or "Unknown"
        shipment.origin = api_data.get("origin") or ""
        shipment.destination = api_data.get("destination") or ""

        eta = parse_api_datetime(api_data.get("eta"))
        ata = parse_api_datetime(api_data.get("ata"))

        if eta:
            shipment.eta = eta

        if ata:
            shipment.ata = ata

        vessels = api_data.get("vessels_table", [])

        current_vessel = next(
            (v.get("vessel") for v in vessels if v.get("is_current")),
            None
        )

        if not current_vessel and vessels:
            current_vessel = vessels[0].get("vessel")

        if current_vessel:
            shipment.vessel = current_vessel

        shipment.lastchecked = timezone.now()
        shipment.save()

        # 3. Save changes detected by our tracker
        if was_checked:

            if old_status != shipment.status:
                shipment.history.create(
                    status="Status Change",
                    description=f"Status changed from {old_status} → {shipment.status}",
                    change_type="Status",
                    old_value=old_status,
                    new_value=shipment.status,
                    event_date=timezone.now(),
                    is_actual=True
                )

            if old_eta != shipment.eta:
                shipment.history.create(
                    status="ETA Change",
                    description=f"ETA changed from {old_eta or 'Unknown'} → {shipment.eta or 'Unknown'}",
                    change_type="ETA",
                    old_value=str(old_eta) if old_eta else "Unknown",
                    new_value=str(shipment.eta) if shipment.eta else "Unknown",
                    event_date=timezone.now(),
                    is_actual=True
                )

            if old_ata != shipment.ata:
                shipment.history.create(
                    status="ATA Change",
                    description=f"ATA changed from {old_ata or 'Unknown'} → {shipment.ata or 'Unknown'}",
                    change_type="ATA",
                    old_value=str(old_ata) if old_ata else "Unknown",
                    new_value=str(shipment.ata) if shipment.ata else "Unknown",
                    event_date=timezone.now(),
                    is_actual=True
                )

        # 4. Save Traqo shipment events
        events = api_data.get("events_table", [])

        for event in events:
            event_id = event.get("event_id")

            if event_id is None:
                continue

            event_id = str(event_id)

            already_saved = shipment.history.filter(
                api_event_id=event_id
            ).exists()

            if not already_saved:
                event_status = (
                    event.get("status_description")
                    or event.get("description")
                    or event.get("status")
                    or "Update"
                )

                shipment.history.create(
                    api_event_id=event_id,
                    event_code=event.get("event_code") or "",
                    status=event_status,
                    description=event.get("description") or "",
                    location=event.get("location") or "",
                    event_date=parse_api_datetime(
                        event.get("timestamp") or event.get("date")
                    ),
                    is_actual=bool(event.get("is_actual"))
                )

        # 5. Send email if Status, ETA, or ATA changed
        if was_checked and (
            old_status != shipment.status
            or old_eta != shipment.eta
            or old_ata != shipment.ata
        ):
            send_mail(
                subject=f"Shipment update: {shipment.name}",
                message=(
                    f"Hello {shipment.user.firstname},\n\n"
                    f"Your shipment '{shipment.name}' has been updated.\n"
                    f"Container: {shipment.number}\n\n"

                    f"Previous status: {old_status}\n"
                    f"Current status: {shipment.status}\n\n"

                    f"Previous ETA: {old_eta or 'Unknown'}\n"
                    f"Current ETA: {shipment.eta or 'Unknown'}\n\n"

                    f"Previous ATA: {old_ata or 'Unknown'}\n"
                    f"Current ATA: {shipment.ata or 'Unknown'}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[shipment.user.email],
                fail_silently=True
            )

        return shipment
    
    def refresh_shipment(self, shipment):
        api_data = fetch_container_data(shipment.number)

        if not api_data:
            return False

        self.save_tracking_data(shipment, api_data)
        return True


    def create_shipment(self, data, user):
        shipment = Shipment.objects.create(
            name=data["name"],
            number=data["number"],
            user=user
        )

        api_data = fetch_container_data(shipment.number)

        if api_data:
            self.save_tracking_data(shipment, api_data)

        return shipment



    def update_shipment(self,data,shipment):
        shipment.name=data['name']
        shipment.number=data['number']
        shipment.save()

    
class User(models.Model):
    firstname=models.CharField(max_length=255)
    lastname=models.CharField(max_length=255)
    email=models.CharField(max_length=255,unique=True)
    password=models.CharField(max_length=255)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    objects=UserManager()

class Shipment(models.Model):
    name=models.CharField(max_length=100)
    number=models.CharField(max_length=20)
    status=models.CharField(max_length=100,default="Unknown")
    eta=models.DateTimeField(null=True,blank=True)
    ata = models.DateTimeField(null=True, blank=True)
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
    description = models.CharField(max_length=255, blank=True)
    event_code = models.CharField(max_length=50, blank=True)
    api_event_id = models.CharField(max_length=100, blank=True)
    event_date = models.DateTimeField(null=True, blank=True)
    is_actual = models.BooleanField(default=False)
     # For changes detected by our tracker
    change_type = models.CharField(max_length=50, blank=True)
    old_value = models.CharField(max_length=255, blank=True)
    new_value = models.CharField(max_length=255, blank=True)
    created_at=models.DateField(auto_now_add=True)