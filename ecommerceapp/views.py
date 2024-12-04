from django.shortcuts import render, redirect
from ecommerceapp.models import Contact, Product, OrderUpdate, Orders
from django.contrib import messages
from math import ceil
from django.views.decorators.csrf import csrf_exempt

# Index View
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nslides), nslides])
    
    params = {'allProds': allProds}
    return render(request, "index.html", params)

# Contact View
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        pnumber = request.POST.get("pnumber")
        myquery = Contact(name=name, email=email, desc=desc, phonenumber=pnumber)
        myquery.save()
        messages.info(request, "We will get back to you soon...")
        return render(request, "contact.html")
    return render(request, "contact.html")

# About View
def about(request):
    return render(request, "about.html")

# Checkout View
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        # Create an order
        order = Orders(
            items_json=items_json,
            name=name,
            amount=amount,
            email=email,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone
        )
        order.save()

        # Update order status to 'PAID' immediately for the dummy payment
        order_update = OrderUpdate(
            order_id=order.order_id,
            update_desc="The order has been placed and payment is successful",
            delivered=False
        )
        order_update.save()

        # Mark the order as PAID (no real payment gateway used here)
        order.oid = str(order.order_id) + "ShopyCart"  # Example order ID
        order.paymentstatus = "PAID"
        order.amountpaid = amount
        order.save()

        # Show success message
        messages.success(request, f"Your order #{order.order_id} has been placed successfully!")
        
        # Redirect to the order summary page (could be a thank you page)
        return redirect('/profile')

    return render(request, 'checkout.html')

# HandleRequest View (Dummy Payment Simulation)
@csrf_exempt
def handlerequest(request):
    # Here, we're just going to simulate a successful payment
    if request.method == "POST":
        # Simulating a successful payment response
        response_dict = {
            'ORDERID': 'dummy123',  # Dummy order ID
            'TXNAMOUNT': '100',  # Dummy payment amount
            'RESPCODE': '01',  # Dummy success response code
            'RESPMSG': 'Success',  # Success message
            'CHECKSUMHASH': 'dummychecksum'  # Dummy checksum (this isn't real)
        }

        # Normally, you would verify the checksum here, but for dummy, we'll skip it
        if response_dict['RESPCODE'] == '01':
            order_id = response_dict['ORDERID']
            amount_paid = response_dict['TXNAMOUNT']
            order = Orders.objects.get(order_id=order_id)

            # Mark the order as paid and update the status
            order.paymentstatus = "PAID"
            order.amountpaid = amount_paid
            order.save()

            # Add an update for the order
            order_update = OrderUpdate(
                order_id=order.order_id,
                update_desc="Payment successful",
                delivered=False
            )
            order_update.save()

            messages.success(request, f"Your order #{order.order_id} has been paid successfully!")
        else:
            messages.error(request, "Payment failed. Please try again.")
        
        return render(request, 'paymentstatus.html', {'response': response_dict})

# Profile View
def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')
    
    currentuser = request.user.username
    items = Orders.objects.filter(email=currentuser)
    
    if not items:
        messages.info(request, "No orders found.")
        return render(request, "profile.html")
    
    order_details = []
    for order in items:
        rid = order.oid.replace("ShopyCart", "")
        status = OrderUpdate.objects.filter(order_id=int(rid))
        order_details.append({
            "order": order,
            "status": status
        })
    
    context = {"order_details": order_details}
    return render(request, "profile.html", context)
