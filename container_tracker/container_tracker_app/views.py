from django.shortcuts import render , HttpResponse,redirect
from .models import *
from .import models
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

            return render(request,"dashboard.html",context)

#display the details of the shipment 
def view_shipment(request,shipment_id):
    if "user_id" not in request.session:
        return redirect("/dashboard")
    else:
        user=User.objects.get(id=request.session['user_id'])

        shipment=Shipment.objects.get(id=shipment_id)

        context={
            "user":user,
            "shipment":shipment
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
            errors=User.objects.shipment_validation(request.POST)
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


#logout view
def logout(request):
    request.session.flush()
    return redirect("/")