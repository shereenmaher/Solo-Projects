from django.db import models
import re
import bcrypt
from datetime import date
import requests
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import json
import os


# =========================================================
# TRAQO API
# =========================================================

# Retrieve data from Traqo when a shipment is first created
def fetch_container_data(number):
    #retrieve the API key from the environment
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


# Retrieve an already tracked shipment from Traqo
def fetch_tracked_shipment(number):
    
    api_key = os.environ.get("TRAQO_API_KEY")

    if not api_key:
        print("Traqo API key is missing")
        return None

    url = (
        f"https://traqocontainer.com/api/v1/"
        f"shipments/{number}?include=full"
    )

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print("Traqo API error:", error)
        return None

    result = response.json()

    if not result.get("success"):
        return None

    data = result.get("data")

    if not data:
        return None

    # include=full puts the stored tracking tables
    # inside "document"
    document = data.get("document")

    if document:

        # Keep the current summary values from Traqo
        # but also give save_tracking_data() the full tables

        data["events_table"] = document.get(
            "events_table",
            []
        )

        data["vessels_table"] = document.get(
            "vessels_table",
            []
        )

    return data


# Handles Traqo's date format(API gives date as text)
def parse_api_datetime(value):

    if not value:
        return None

    parsed = parse_datetime(
        value.replace(" ", "T", 1)
    )

    if parsed and timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)

    return parsed


# =========================================================
# USER MANAGER
# =========================================================

class UserManager(models.Manager):

    # Register validation
    def reg_validation(self, data):

        errors = {}

        firstname = data['firstname']
        lastname = data['lastname']
        email = data['email']
        password = data['password']
        confirm_pw = data['confirm_pw']

        if len(firstname) == 0:
            errors['firstnameerror'] = "firstname is required"

        if len(lastname) == 0:
            errors['lastnameerror'] = "lastname is required"

        if len(email) == 0:
            errors['emailerror'] = "email is required"

        if len(password) == 0:
            errors['passworderror'] = "password is required"

        if len(firstname) < 2:
            errors['firstnameerror'] = (
                "firstname must be at least 2 chars"
            )

        if len(lastname) < 2:
            errors['lastnameerror'] = (
                "lastname must be at least 2 chars"
            )

        if len(password) < 8:
            errors['passworderror'] = (
                "password must be at least 8 chars"
            )

        EMAIL_REGEX = re.compile(
            r'^[a-zA-Z0-9.+\_-]+@[a-zA-Z0-9.\_-]+\.[a-zA-Z]+$'
        )

        if email and not EMAIL_REGEX.match(email):
            errors['emailerror'] = "email is invalid"

        if password != confirm_pw:
            errors['confirm_pwerror'] = (
                "passwords do not match"
            )

        if email and User.objects.filter(
            email=email
        ).exists():

            errors['emailerror'] = (
                "email already exists"
            )

        return errors


    def create_user(self, data):

        firstname = data['firstname']
        lastname = data['lastname']
        email = data['email']
        password = data['password']

        pw_hash = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        user = User.objects.create(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=pw_hash
        )

        return user


    def login_validation(self, data):

        errors = {}

        email = data['email']
        password = data['password']

        if len(email) == 0:
            errors['loginemailerror'] = (
                "email is required"
            )

        if len(password) == 0:
            errors['loginpassworderror'] = (
                "password is required"
            )

        if len(errors) == 0:

            user = User.objects.filter(
                email=email
            )

            if user:

                logged_user = user[0]

                if not bcrypt.checkpw(
                    password.encode(),
                    logged_user.password.encode()
                ):

                    errors['loginerror'] = (
                        "invalid email or paswword"
                    )

            # When user does not exist
            else:

                errors['loginerror'] = (
                    "invalid email or paswword"
                )

        return errors


    def login_user(self, data):

        errors = self.login_validation(data)

        if len(errors) == 0:

            email = data['email']

            user = User.objects.get(
                email=email
            )

            return user

        return None


# =========================================================
# SHIPMENT MANAGER
# =========================================================

class shipmentManager(models.Manager):

    # Shipment validation
    def shipment_validation(self, data):

        errors = {}

        name = data['name']
        number = data['number']

        if len(name) == 0:
            errors['nameerror'] = (
                "name is required"
            )

        if len(number) == 0:
            errors['numbererror'] = (
                "number is required"
            )

        elif len(name) < 5:
            errors['nameerror'] = (
                "name must be at least 4 characters"
            )

        elif len(number) != 11:
            errors['numbererror'] = (
                "number must be 11 characters"
            )

        if not re.fullmatch(
            r'[A-Z]{4}[0-9]{7}',
            number
        ):

            errors['numbererror'] = (
                "Invalid container number format"
            )

        return errors


    # =====================================================
    # SAVE TRACKING DATA
    # =====================================================

    def save_tracking_data(
        self,
        shipment,
        api_data
    ):

        # 1. Save OLD values before updating shipment

        old_status = shipment.status
        old_eta = shipment.eta
        old_ata = shipment.ata

        was_checked = (
            shipment.lastchecked is not None
        )


        # 2. Update current shipment information

        shipment.status = (
            api_data.get("status")
            or "Unknown"
        )

        shipment.origin = (
            api_data.get("origin")
            or ""
        )

        shipment.destination = (
            api_data.get("destination")
            or ""
        )


        eta = parse_api_datetime(
            api_data.get("eta")
        )

        ata = parse_api_datetime(
            api_data.get("ata")
        )


        # ETA can change
        if eta:
            shipment.eta = eta


        # ATA should only be saved once
        if ata and not shipment.ata:
            shipment.ata = ata


        # Get vessel information

        vessels = api_data.get(
            "vessels_table",
            []
        )

        current_vessel = next(

            (
                v.get("vessel")
                for v in vessels
                if v.get("is_current")
            ),

            None
        )

        if not current_vessel and vessels:

            current_vessel = (
                vessels[0].get("vessel")
            )

        if current_vessel:

            shipment.vessel = (
                current_vessel
            )


        # Update last checked

        shipment.lastchecked = (
            timezone.now()
        )

        shipment.save()


        # =================================================
        # 3. SAVE CHANGES DETECTED BY OUR TRACKER
        # =================================================

        if was_checked:


            # STATUS CHANGE

            if old_status != shipment.status:

                shipment.history.create(

                    status="Status Change",

                    description=(
                        f"Status changed from "
                        f"{old_status} → "
                        f"{shipment.status}"
                    ),

                    change_type="Status",

                    old_value=old_status,

                    new_value=shipment.status,

                    event_date=timezone.now(),

                    is_actual=True
                )


            # ETA CHANGE

            if old_eta != shipment.eta:


                if old_eta:

                    old_eta_display = (
                        timezone.localtime(
                            old_eta
                        ).strftime(
                            "%b %d, %Y %H:00"
                        )
                    )

                else:

                    old_eta_display = (
                        "Unknown"
                    )


                if shipment.eta:

                    new_eta_display = (
                        timezone.localtime(
                            shipment.eta
                        ).strftime(
                            "%b %d, %Y %H:00"
                        )
                    )

                else:

                    new_eta_display = (
                        "Unknown"
                    )


                shipment.history.create(

                    status="ETA Change",

                    description=(
                        f"ETA changed from "
                        f"{old_eta_display} → "
                        f"{new_eta_display}"
                    ),

                    change_type="ETA",

                    old_value=old_eta_display,

                    new_value=new_eta_display,

                    event_date=timezone.now(),

                    is_actual=True
                )


            # ACTUAL ARRIVAL

            if old_ata != shipment.ata:

                if shipment.ata:

                    ata_display = (
                        timezone.localtime(
                            shipment.ata
                        ).strftime(
                            "%b %d, %Y %H:00"
                        )
                    )

                else:

                    ata_display = (
                        "Unknown"
                    )


                shipment.history.create(

                    status="Actual Arrival",

                    description=(
                        f"Actual arrival recorded: "
                        f"{ata_display}"
                    ),

                    change_type="ATA",

                    old_value="Not arrived",

                    new_value=ata_display,

                    event_date=timezone.now(),

                    is_actual=True
                )


        # =================================================
        # 4. SAVE TRAQO SHIPMENT EVENTS
        # =================================================

        events = api_data.get(
            "events_table",
            []
        )

        for event in events:

            event_id = event.get(
                "event_id"
            )

            if event_id is None:
                continue

            event_id = str(
                event_id
            )


            # Check if event already exists

            already_saved = (
                shipment.history.filter(
                    api_event_id=event_id
                ).exists()
            )

            if not already_saved:

                event_status = (

                    event.get(
                        "status_description"
                    )

                    or event.get(
                        "description"
                    )

                    or event.get(
                        "status"
                    )

                    or "Update"
                )


                shipment.history.create(

                    api_event_id=event_id,

                    event_code=(
                        event.get(
                            "event_code"
                        )
                        or ""
                    ),

                    status=event_status,

                    description=(
                        event.get(
                            "description"
                        )
                        or ""
                    ),

                    location=(
                        event.get(
                            "location"
                        )
                        or ""
                    ),

                    event_date=(
                        parse_api_datetime(

                            event.get(
                                "timestamp"
                            )

                            or event.get(
                                "date"
                            )
                        )
                    ),

                    is_actual=bool(
                        event.get(
                            "is_actual"
                        )
                    )
                )

        return shipment


    # =====================================================
    # REFRESH SHIPMENT
    # =====================================================

    def refresh_shipment(
        self,
        shipment
    ):

        api_data = (
            fetch_tracked_shipment(
                shipment.number
            )
        )

        if not api_data:
            return False

        self.save_tracking_data(
            shipment,
            api_data
        )

        return True


    # =====================================================
    # CREATE SHIPMENT
    # =====================================================

    def create_shipment(
        self,
        data,
        user
    ):

        shipment = Shipment.objects.create(

            name=data["name"],

            number=data["number"],

            user=user
        )


        # Create document checklist

        ShipmentDocuments.objects.create(
            shipment=shipment
        )


        # NEW:
        # Create landed cost record

        LandedCost.objects.create(
            shipment=shipment
        )


        # Get initial Traqo information

        api_data = (
            fetch_container_data(
                shipment.number
            )
        )

        if api_data:

            self.save_tracking_data(
                shipment,
                api_data
            )

        return shipment


    # =====================================================
    # UPDATE SHIPMENT
    # =====================================================

    def update_shipment(
        self,
        data,
        shipment
    ):

        shipment.name = (
            data['name']
        )

        shipment.number = (
            data['number']
        )

        shipment.save()


# =========================================================
# USER MODEL
# =========================================================

class User(models.Model):

    firstname = models.CharField(
        max_length=255
    )

    lastname = models.CharField(
        max_length=255
    )

    email = models.CharField(
        max_length=255,
        unique=True
    )

    password = models.CharField(
        max_length=255
    )

    created_at = models.DateField(
        auto_now_add=True
    )

    updated_at = models.DateField(
        auto_now=True
    )

    objects = UserManager()


# =========================================================
# SHIPMENT MODEL
# =========================================================

class Shipment(models.Model):

    name = models.CharField(
        max_length=100
    )

    number = models.CharField(
        max_length=20
    )

    status = models.CharField(
        max_length=100,
        default="Unknown"
    )

    eta = models.DateTimeField(
        null=True,
        blank=True
    )

    ata = models.DateTimeField(
        null=True,
        blank=True
    )

    vessel = models.CharField(
        max_length=150,
        blank=True
    )

    origin = models.CharField(
        max_length=150,
        blank=True
    )

    destination = models.CharField(
        max_length=150,
        blank=True
    )

    lastchecked = models.DateTimeField(
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        User,
        related_name="shipments",
        on_delete=models.DO_NOTHING
    )

    created_at = models.DateField(
        auto_now_add=True
    )

    updated_at = models.DateField(
        auto_now=True
    )

    objects = shipmentManager()


    # Used by Document Risk feature

    def days_until_arrival(self):

        if not self.eta:
            return None

        difference = (
            self.eta
            - timezone.now()
        )

        return difference.days


# =========================================================
# SHIPMENT HISTORY MODEL
# =========================================================

class shipmentHistory(models.Model):

    shipment = models.ForeignKey(
        Shipment,
        related_name='history',
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=100
    )

    location = models.CharField(
        max_length=150,
        blank=True
    )

    eta = models.DateTimeField(
        null=True,
        blank=True
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    event_code = models.CharField(
        max_length=50,
        blank=True
    )

    api_event_id = models.CharField(
        max_length=100,
        blank=True
    )

    event_date = models.DateTimeField(
        null=True,
        blank=True
    )

    is_actual = models.BooleanField(
        default=False
    )


    # For changes detected by our tracker

    change_type = models.CharField(
        max_length=50,
        blank=True
    )

    old_value = models.CharField(
        max_length=255,
        blank=True
    )

    new_value = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateField(
        auto_now_add=True
    )


# =========================================================
# SHIPMENT DOCUMENTS MODEL
# =========================================================

class ShipmentDocuments(models.Model):

    commercial_invoice = (
        models.BooleanField(
            default=False
        )
    )

    packing_list = (
        models.BooleanField(
            default=False
        )
    )

    bill_of_lading = (
        models.BooleanField(
            default=False
        )
    )

    certificate_of_origin = (
        models.BooleanField(
            default=False
        )
    )

    insurance = (
        models.BooleanField(
            default=False
        )
    )

    customs_declaration = (
        models.BooleanField(
            default=False
        )
    )

    shipment = models.OneToOneField(

        Shipment,

        related_name="documents",

        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def readiness_percentage(self):

        documents = [

            self.commercial_invoice,

            self.packing_list,

            self.bill_of_lading,

            self.certificate_of_origin,

            self.insurance,

            self.customs_declaration
        ]

        completed = (
            documents.count(True)
        )

        return round(
            (
                completed
                / len(documents)
            )
            * 100
        )


    def missing_count(self):

        documents = [

            self.commercial_invoice,

            self.packing_list,

            self.bill_of_lading,

            self.certificate_of_origin,

            self.insurance,

            self.customs_declaration
        ]

        return documents.count(
            False
        )


# =========================================================
# LANDED COST MODEL
# =========================================================

class LandedCost(models.Model):

    shipment = models.OneToOneField(
        Shipment,
        related_name="landed_cost",
        on_delete=models.CASCADE
    )


    # Purchase value of the goods

    goods_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    # Ocean shipping cost

    ocean_freight = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    # Customs / import duties

    customs_duties = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    # Cargo insurance

    insurance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    # Transport from port to warehouse

    local_transport = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    # Any additional shipment costs

    other_costs = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    # Number of units in this shipment

    quantity = models.PositiveIntegerField(
        default=0
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    # Total shipment cost after import expenses

    def total_landed_cost(self):

        return (
            self.goods_value
            + self.ocean_freight
            + self.customs_duties
            + self.insurance
            + self.local_transport
            + self.other_costs
        )


    # Cost of one unit after all import expenses

    def cost_per_unit(self):

        if self.quantity == 0:
            return 0

        return (
            self.total_landed_cost()
            / self.quantity
        )