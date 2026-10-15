from django.shortcuts import render , HttpResponse,redirect
from .models import *
from .import models
from django.views.decorators.http import require_POST

#show the register/login page
def reg_log_page(request):
    return render(request,"reg_log.html")

#register (validate user info and redirect to dashboard)
def register(request):
    if request.method == 'POST':

        errors=User.objects.reg_validation(request.POST)

        if len(errors) > 0 :
            context={
                "errors":errors
            }
            return render(request,"reg_log.html",context)

        else:
            user=User.objects.create_user(request.POST)
            request.session['user_id']=user.id

            return redirect("/dashboard")

    else:
        return redirect("/")
    
#log in (validate user info and redirects to dashboard)
def login(request):
    if request.method == 'POST':
    
            errors=User.objects.login_validation(request.POST)
    
            if len(errors) > 0 :
                context={
                    "errors":errors
                }
                return render(request,"reg_log.html",context)
            else:
                user=User.objects.login_user(request.POST)
                request.session['user_id']=user.id
            return redirect("/dashboard")
    else:
        return redirect("/")

#check if user logged in and bring all shipments from database and show them on dashboard
def shipments(request):
    if "user_id" not in request.session:
        return redirect("/")
    else:
        user=User.objects.get(id=request.session['user_id'])
        shipments=Shipment.objects.all()

        context={
            "user":user,
            "shipments":shipments
        }
        return render(request,"dashboard.html",context)

#create shipment if user logged in 
def create_shipment(request):

    if "user_id" not in request.session:

        return redirect("/")

    else:

        user = User.objects.get(
            id=request.session["user_id"]
        )

        if request.method == "POST":

            errors = Shipment.objects.shipment_validation(request.POST)

            if len(errors) > 0:

                context = {
                    "user": user,
                    "errors": errors
                }

                return render(request,"createshipment.html",context)

            else:
                user = User.objects.get( id=request.session["user_id"] )
                Shipment.objects.create_shipment(request.POST,user)

                return redirect("/dashboard")

        else:

            context = {
                "user": user
            }

            return render(request,"createshipment.html",context)

#display the details of the shipment 
def view_shipment(request,shipment_id):
    if "user_id" not in request.session:
        return redirect("/dashboard")
    else:
        user=User.objects.get(id=request.session['user_id'])

        shipment=Shipment.objects.get(id=shipment_id)
        documents, created = ShipmentDocuments.objects.get_or_create(shipment=shipment)
        context={
            "user":user,
            "shipment":shipment,
            "documents": documents
        }
        return render(request,"shipmentdetails.html",context)

#edit shipemnt
def edit_shipment(request,shipment_id):
    if "user_id" not in request.session:
        return redirect("/dashboard")
    else:
        user=User.objects.get(id=request.session['user_id'])

        shipment=Shipment.objects.get(id=shipment_id)

        if shipment.user.id != user.id:
            return redirect("/dashboard")

        if request.method == 'POST': 
            errors=Shipment.objects.shipment_validation(request.POST)
            if len(errors) > 0 :
                context={
                    "user":user,
                    "shipment":shipment,
                    "errors":errors
                }
                return render(request,"editshipment.html",context)
            else:
                Shipment.objects.update_shipment(request.POST,shipment)
                return redirect("/dashboard")
        else:
            context={
                "user":user,
                "shipment":shipment,
            }
            return render(request,"editshipment.html",context)

#shipment history

def shipment_history(request, shipment_id):
    if "user_id" not in request.session:
        return redirect("/")

    user = User.objects.filter(
        id=request.session["user_id"]
    ).first()

    if user is None:
        request.session.flush()
        return redirect("/")

    shipment = Shipment.objects.filter(id=shipment_id).first()

    if shipment is None:
        return redirect("/dashboard")

    history = shipment.history.all().order_by(
        "-event_date", "-created_at"
    )

    context = {
        "user": user,
        "shipment": shipment,
        "history": history
    }

    return render(request, "shipmenthistory.html", context)


#Connect the Refresh button

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

    shipment = Shipment.objects.filter(id=shipment_id).first()

    if shipment is None:
        return redirect("/dashboard")

    refreshed = Shipment.objects.refresh_shipment(shipment)

    if not refreshed:
        # The refresh failed; keep the existing saved data.
        return redirect("view_shipment", shipment_id=shipment.id)

    return redirect("view_shipment", shipment_id=shipment.id)

#shipment documents
def edit_shipment_documents(request, shipment_id):

    if "user_id" not in request.session:
        return redirect("/")

    shipment = Shipment.objects.get(id=shipment_id)

    documents, created = ShipmentDocuments.objects.get_or_create(
        shipment=shipment
    )

    if request.method == "POST":

        documents.commercial_invoice = (
            "commercial_invoice" in request.POST
        )

        documents.packing_list = (
            "packing_list" in request.POST
        )

        documents.bill_of_lading = (
            "bill_of_lading" in request.POST
        )

        documents.certificate_of_origin = (
            "certificate_of_origin" in request.POST
        )

        documents.insurance = (
            "insurance" in request.POST
        )

        documents.customs_declaration = (
            "customs_declaration" in request.POST
        )

        documents.save()

        return redirect(
            "view_shipment",
            shipment_id=shipment.id
        )

    context = {
        "shipment": shipment,
        "documents": documents
    }

    return render(
        request,
        "edit_shipment_documents.html",
        context
    )

#logout view
def logout(request):
    request.session.flush()
    return redirect("/")