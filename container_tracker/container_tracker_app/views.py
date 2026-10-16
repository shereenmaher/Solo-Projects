from django.shortcuts import render, HttpResponse, redirect
from .models import *
from . import models
from django.views.decorators.http import require_POST


# =========================================================
# REGISTER / LOGIN PAGE
# =========================================================

def reg_log_page(request):
    return render(request, "reg_log.html")


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.method == 'POST':

        errors = User.objects.reg_validation(
            request.POST
        )

        if len(errors) > 0:

            context = {
                "errors": errors
            }

            return render(
                request,
                "reg_log.html",
                context
            )

        else:

            user = User.objects.create_user(
                request.POST
            )

            request.session['user_id'] = user.id

            return redirect("/dashboard")

    else:

        return redirect("/")


# =========================================================
# LOGIN
# =========================================================

def login(request):

    if request.method == 'POST':

        errors = User.objects.login_validation(
            request.POST
        )

        if len(errors) > 0:

            context = {
                "errors": errors
            }

            return render(
                request,
                "reg_log.html",
                context
            )

        else:

            user = User.objects.login_user(
                request.POST
            )

            request.session['user_id'] = user.id

            return redirect("/dashboard")

    else:

        return redirect("/")


# =========================================================
# DASHBOARD / ALL SHIPMENTS
# =========================================================

def shipments(request):

    if "user_id" not in request.session:

        return redirect("/")

    else:

        user = User.objects.get(
            id=request.session['user_id']
        )

        shipments = Shipment.objects.all()

        context = {
            "user": user,
            "shipments": shipments
        }

        return render(
            request,
            "dashboard.html",
            context
        )


# =========================================================
# CREATE SHIPMENT
# =========================================================

def create_shipment(request):

    if "user_id" not in request.session:

        return redirect("/")

    else:

        user = User.objects.get(
            id=request.session["user_id"]
        )

        if request.method == "POST":

            errors = (
                Shipment.objects.shipment_validation(
                    request.POST
                )
            )

            if len(errors) > 0:

                context = {
                    "user": user,
                    "errors": errors
                }

                return render(
                    request,
                    "createshipment.html",
                    context
                )

            else:

                Shipment.objects.create_shipment(
                    request.POST,
                    user
                )

                return redirect("/dashboard")

        else:

            context = {
                "user": user
            }

            return render(
                request,
                "createshipment.html",
                context
            )


# =========================================================
# SHIPMENT DETAILS
# =========================================================

def view_shipment(request, shipment_id):

    if "user_id" not in request.session:

        return redirect("/")

    else:

        user = User.objects.get(
            id=request.session['user_id']
        )

        shipment = Shipment.objects.get(
            id=shipment_id
        )


        # Get or create document checklist

        documents, created = (
            ShipmentDocuments.objects.get_or_create(
                shipment=shipment
            )
        )


        # Get or create landed cost information
        # This also handles shipments that existed
        # before we added the LandedCost model.

        landed_cost, created = (
            LandedCost.objects.get_or_create(
                shipment=shipment
            )
        )


        context = {

            "user": user,

            "shipment": shipment,

            "documents": documents,

            "landed_cost": landed_cost
        }


        return render(
            request,
            "shipmentdetails.html",
            context
        )


# =========================================================
# EDIT SHIPMENT
# =========================================================

def edit_shipment(request, shipment_id):

    if "user_id" not in request.session:

        return redirect("/")

    else:

        user = User.objects.get(
            id=request.session['user_id']
        )

        shipment = Shipment.objects.get(
            id=shipment_id
        )


        # Only shipment creator can edit

        if shipment.user.id != user.id:

            return redirect("/dashboard")


        if request.method == 'POST':

            errors = (
                Shipment.objects.shipment_validation(
                    request.POST
                )
            )


            if len(errors) > 0:

                context = {

                    "user": user,

                    "shipment": shipment,

                    "errors": errors
                }

                return render(
                    request,
                    "editshipment.html",
                    context
                )

            else:

                Shipment.objects.update_shipment(
                    request.POST,
                    shipment
                )

                return redirect("/dashboard")

        else:

            context = {

                "user": user,

                "shipment": shipment
            }

            return render(
                request,
                "editshipment.html",
                context
            )


# =========================================================
# SHIPMENT HISTORY
# =========================================================

def shipment_history(request, shipment_id):

    if "user_id" not in request.session:

        return redirect("/")


    user = User.objects.filter(
        id=request.session["user_id"]
    ).first()


    if user is None:

        request.session.flush()

        return redirect("/")


    shipment = Shipment.objects.filter(
        id=shipment_id
    ).first()


    if shipment is None:

        return redirect("/dashboard")


    history = (
        shipment.history.all().order_by(
            "-event_date",
            "-created_at"
        )
    )


    context = {

        "user": user,

        "shipment": shipment,

        "history": history
    }


    return render(
        request,
        "shipmenthistory.html",
        context
    )


# =========================================================
# REFRESH SHIPMENT
# =========================================================

@require_POST
def refresh_shipment(request, shipment_id):

    if "user_id" not in request.session:

        return redirect("/")


    user = User.objects.filter(
        id=request.session["user_id"]
    ).first()


    if user is None:

        request.session.flush()

        return redirect("/")


    shipment = Shipment.objects.filter(
        id=shipment_id
    ).first()


    if shipment is None:

        return redirect("/dashboard")


    refreshed = (
        Shipment.objects.refresh_shipment(
            shipment
        )
    )


    if not refreshed:

        # Refresh failed.
        # Keep existing saved data.

        return redirect(
            "view_shipment",
            shipment_id=shipment.id
        )


    return redirect(
        "view_shipment",
        shipment_id=shipment.id
    )


# =========================================================
# SHIPMENT DOCUMENTS
# =========================================================

def edit_shipment_documents(
    request,
    shipment_id
):

    if "user_id" not in request.session:

        return redirect("/")


    user = User.objects.get(
        id=request.session["user_id"]
    )


    shipment = Shipment.objects.get(
        id=shipment_id
    )


    # Only shipment creator can edit documents

    if shipment.user.id != user.id:

        return redirect(
            "view_shipment",
            shipment_id=shipment.id
        )


    documents, created = (
        ShipmentDocuments.objects.get_or_create(
            shipment=shipment
        )
    )


    if request.method == "POST":


        documents.commercial_invoice = (
            "commercial_invoice"
            in request.POST
        )


        documents.packing_list = (
            "packing_list"
            in request.POST
        )


        documents.bill_of_lading = (
            "bill_of_lading"
            in request.POST
        )


        documents.certificate_of_origin = (
            "certificate_of_origin"
            in request.POST
        )


        documents.insurance = (
            "insurance"
            in request.POST
        )


        documents.customs_declaration = (
            "customs_declaration"
            in request.POST
        )


        documents.save()


        return redirect(
            "view_shipment",
            shipment_id=shipment.id
        )


    context = {

        "user": user,

        "shipment": shipment,

        "documents": documents
    }


    return render(
        request,
        "edit_shipment_documents.html",
        context
    )


# =========================================================
# LANDED COST
# =========================================================

def edit_landed_cost(
    request,
    shipment_id
):

    if "user_id" not in request.session:

        return redirect("/")


    user = User.objects.get(
        id=request.session["user_id"]
    )


    shipment = Shipment.objects.get(
        id=shipment_id
    )


    # Only shipment creator can edit landed costs

    if shipment.user.id != user.id:

        return redirect(
            "view_shipment",
            shipment_id=shipment.id
        )


    # get_or_create is important because older
    # shipments do not already have a LandedCost record

    landed_cost, created = (
        LandedCost.objects.get_or_create(
            shipment=shipment
        )
    )


    if request.method == "POST":


        # If a field is empty, save 0

        goods_value = (
            request.POST["goods_value"]
            or 0
        )

        ocean_freight = (
            request.POST["ocean_freight"]
            or 0
        )

        customs_duties = (
            request.POST["customs_duties"]
            or 0
        )

        insurance = (
            request.POST["insurance"]
            or 0
        )

        local_transport = (
            request.POST["local_transport"]
            or 0
        )

        other_costs = (
            request.POST["other_costs"]
            or 0
        )

        quantity = (
            request.POST["quantity"]
            or 0
        )


        landed_cost.goods_value = (
            goods_value
        )

        landed_cost.ocean_freight = (
            ocean_freight
        )

        landed_cost.customs_duties = (
            customs_duties
        )

        landed_cost.insurance = (
            insurance
        )

        landed_cost.local_transport = (
            local_transport
        )

        landed_cost.other_costs = (
            other_costs
        )

        landed_cost.quantity = (
            quantity
        )


        landed_cost.save()


        return redirect(
            "view_shipment",
            shipment_id=shipment.id
        )


    context = {

        "user": user,

        "shipment": shipment,

        "landed_cost": landed_cost
    }


    return render(
        request,
        "edit_landed_cost.html",
        context
    )


# =========================================================
# LOGOUT
# =========================================================

def logout(request):

    request.session.flush()

    return redirect("/")