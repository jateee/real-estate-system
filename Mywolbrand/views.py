import requests
from .forms import ContactForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login  
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from .models import Order, Profile
from .forms import ProfileUpdateForm
from .forms import SellItemForm
from .models import SellItem
from .forms import PartnerApplicationForm
from django.http import JsonResponse
from .models import PropertyType
from .forms import RenovationRequestForm
from .models import PropertyDevelopmentRequest
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserConsent
from django.utils import timezone
from .models import Property
from django.db.models import Q
from .models import SellItem, Bid, CartItem
from coinbase_commerce.client import Client
from coinbase_commerce.error import APIError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from coinbase_commerce.webhook import Webhook
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .mpesa import stk_push
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Bid, Property
from .models import SellItem
from django.urls import reverse
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.db.models import Q
from django.core.paginator import Paginator





def index(request):
    return render(request, "Mywolbrand/index.html")  

def homepage(request):
    return render(request, "Mywolbrand/index.html")  
    

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user) 
            return redirect("dashboard") 
    else:
        form = RegisterForm()
    return render(request, "Mywolbrand/register.html", {"form": form})

def login(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("dashboard")
    else:
        form = LoginForm()
    return render(request, "Mywolbrand/login.html", {"form": form})




@login_required
def dashboard(request):
    # Items posted by the logged-in user
    my_items_qs = SellItem.objects.filter(user=request.user).order_by('-created_at')
    
    # All items from all users (including current user)
    all_items_qs = SellItem.objects.all().order_by('-created_at')

    # Handle search query / Get query parameters
    query = request.GET.get('query', '').strip()
    property_type = request.GET.get('property_type', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    # Apply filters to all_items
    if query:
        all_items_qs = all_items_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(category__icontains=query) |
            Q(house_type__icontains=query) |
            Q(price__icontains=query) |
            Q(final_price__icontains=query)
        )

    if property_type:
        all_items_qs = all_items_qs.filter(house_type__iexact=property_type)

    if max_price:
        try:
            all_items_qs = all_items_qs.filter(final_price__lte=float(max_price))
        except ValueError:
            pass  # Ignore invalid input

    # Apply pagination
    paginator_all = Paginator(all_items_qs, 12)  # show 12 per page
    page_number_all = request.GET.get("page_all")
    all_items = paginator_all.get_page(page_number_all)

    paginator_my = Paginator(my_items_qs, 4)     # 8 per page for my items
    page_number_my = request.GET.get("page_my")
    my_items = paginator_my.get_page(page_number_my)

    context = {
        "my_items": my_items,
        "all_items": all_items,
        "request": request,  # Needed for pre-filling the search form
    }
    
    return render(request, "Mywolbrand/dashboard.html", context)


 

def logout_view(request):
    logout(request)
    return redirect("index")


def contactus(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect("contactus")
    else:
        form = ContactForm()
    return render(request, "Mywolbrand/contactus.html", {"form": form})




@login_required
def sell(request):
    if request.method == "POST":
        form = SellItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user  # Associate item with current user
            item.save()
            messages.success(request, "Your item has been listed successfully!")
            return redirect("dashboard")  # Go to dashboard after listing
    else:
        form = SellItemForm()
    
    return render(request, "Mywolbrand/sell.html", {"form": form})



@login_required
def request_contact(request, item_id):
    item = get_object_or_404(SellItem, id=item_id)

    item.contact_requested.add(request.user) 
    # Mark the item as requested
    item.contact_requested = True
    item.save()

 
    messages.success(request, "Your request has been sent to the admin. They will contact you soon.")
    return redirect('dashboard')


@login_required
def myprofile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        id_card = request.FILES.get("id_card")

        # Validate required fields
        if not first_name or not last_name or not phone:
            messages.error(request, "First name, Last name, and Phone are required.")
            return redirect("myprofile")

        # Update user info
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Update profile info
        profile.phone = phone
        if id_card:  # make ID card optional (doesn’t force re-upload)
            profile.id_card = id_card
        profile.save()

        # Success message
        messages.success(request, "Your profile has been updated successfully.")
        return redirect("myprofile")

    return render(request, "Mywolbrand/myprofile.html", {"profile": profile})

@login_required
def sell_property(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        category = request.POST.get("category")
        location = request.POST.get("location")
        house_type = request.POST.get("house_type")
        image = request.FILES.get("image")
        ownership_proof = request.FILES.get("ownership_proof")

        item = SellItem.objects.create(
            user=request.user,
            title=title,
            description=description,
            price=price,
            category=category,
            location=location,
            house_type=house_type,
            image=image,
            ownership_proof=ownership_proof
        )
        messages.success(request, f"{item.title} has been listed successfully.")
        return redirect("dashboard")

    return render(request, "Mywolbrand/sell.html")



def become_partner(request):
    if request.method == "POST":
        form = PartnerApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! We’ll review your application soon.")
            return redirect("become_partner")
    else:
        form = PartnerApplicationForm()

    return render(request, "Mywolbrand/become_partner.html", {"form": form})




def property_development(request):
    if request.method == "POST":
        property_type = request.POST.get("property_type")
        residential_type = request.POST.get("residential_type")
        commercial_type = request.POST.get("commercial_type")
        land_type = request.POST.get("land_type")
        phone = request.POST.get("phone")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        details = request.POST.get("details")

        # Save to database
        PropertyDevelopmentRequest.objects.create(
            property_type=property_type,
            residential_type=residential_type,
            commercial_type=commercial_type,
            land_type=land_type,
            phone=phone,
            full_name=full_name,
            email=email,
            details=details,
            
        )

        messages.success(request, "Your request has been submitted successfully!")
        return redirect("property_development")  # reload the form

    return render(request, "Mywolbrand/property_development.html")
    

    

def investment_education(request):
    return render(request, "Mywolbrand/investment_education.html")



def privacy_policy(request):
    context = {
        "site_name": "Wolbrand.Inn",
        "effective_date": date.today().strftime("%Y-%m-%d"), 
        "contact_email": "privacy@mywebsite.com",
        "data_controller_name": "Wolbrand.Inn Ltd.",
        "company_address": "123 Business St, City, Country",
    }
    return render(request, "Mywolbrand/privacy_policy.html", context)


def terms_of_service(request):
    context = {
        "site_name": "Wolbrand.Inn Real Estate Platform",
        "effective_date": date.today().strftime("%Y-%m-%d"), 
        "contact_email": "support@myrealestate.co.ke",
        "data_controller_name": "Wolbrand.Inn Ltd",
        "company_address": "Nairobi, Kenya",
    }
    return render(request, "Mywolbrand/terms_of_service.html", context) 




@receiver(post_save, sender=User)
def create_user_consent(sender, instance, created, **kwargs):
    if created:
        UserConsent.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_consent(sender, instance, **kwargs):
    instance.consent.save()
 




def interior_fitting(request):
    
    return render(request, 'Mywolbrand/interior_fitting.html')




@login_required
def place_bid(request, property_id):
    property_obj = get_object_or_404(SellItem, id=property_id)

    if request.method == "POST":
        amount = request.POST.get("amount")
        if amount:
            try:
                amount = float(amount)
                highest_bid = Bid.objects.filter(property=property_obj).order_by('-amount').first()
                if highest_bid and amount <= highest_bid.amount:
                    messages.error(request, f"Your bid must be higher than the current highest bid of {highest_bid.amount}.")
                else:
                    Bid.objects.create(user=request.user, property=property_obj, amount=amount)
                    messages.success(request, f"Your bid of {amount} has been placed on {property_obj.title}.")
            except ValueError:
                messages.error(request, "Please enter a valid number for your bid.")
        else:
            messages.error(request, "Please enter a bid amount.")

    return redirect('dashboard')





@login_required
def add_to_cart(request, property_id):
    property_obj = get_object_or_404(SellItem, id=property_id)

    # Prevent duplicate items
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        property=property_obj
    )

    if created:
        messages.success(request, f"{property_obj.title} has been added to your cart.")
    else:
        messages.info(request, f"{property_obj.title} is already in your cart.")

    return redirect("dashboard")



@login_required
def my_bids(request):
    my_bids = Bid.objects.filter(user=request.user).select_related('property')
    return render(request, "Mywolbrand/my_bids.html", {"my_bids": my_bids})



@login_required
def property_detail(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    return render(request, "Mywolbrand/property_detail.html", {"property": property_obj})   


@login_required
def my_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related("property")
    cart_total = sum(item.property.price for item in cart_items)

    return render(
        request,
        "Mywolbrand/my_cart.html",
        {"cart_items": cart_items, "cart_total": cart_total}
    )




def faq(request):
    return render(request, "Mywolbrand/faq.html")



client = Client(api_key=settings.COINBASE_COMMERCE_API_KEY)

@login_required
def create_crypto_payment(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related("property")

    if not cart_items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("my_cart")

    # Calculate total
    cart_total = sum(item.property.price for item in cart_items)

    try:
        charge_data = {
            'name': 'Wolbrand Checkout',
            'description': f'Payment for {len(cart_items)} item(s)',
            'local_price': {
                'amount': str(cart_total),
                'currency': 'USD'
            },
            'pricing_type': 'fixed_price',
            # Optional metadata to track user/order
            'metadata': {
                'user_id': request.user.id,
            }
        }
        charge = client.charge.create(**charge_data)
        return redirect(charge['hosted_url'])
    except APIError as e:
        return render(request, 'Mywolbrand/my_cart.html', {'error': str(e)})



@csrf_exempt
def coinbase_webhook(request):
    payload = request.body
    signature = request.META.get('HTTP_X_CC_WEBHOOK_SIGNATURE', '')

    try:
        event = Webhook.construct_event(payload, signature, 'your_webhook_shared_secret')

        if event['type'] == 'charge:confirmed':
            metadata = event['data']['metadata']
            user_id = metadata.get('user_id')

            # Mark user’s latest pending order as paid
            Order.objects.filter(user_id=user_id, status="pending").update(status="paid")

            print("✅ Payment confirmed and order updated.")
    except Exception as e:
        return HttpResponse(status=400)

    return HttpResponse(status=200)

  

@csrf_exempt
def initiate_payment(request):
    """
    Initiates an STK Push request to Safaricom M-Pesa.
    URL: /initiate/?phone=2547XXXXXXX&amount=500
    """
    phone = request.GET.get("phone")
    amount = request.GET.get("amount")

    if not phone or not amount:
        return JsonResponse({"error": "Phone and amount are required"}, status=400)

    try:
        amount = float(amount)
    except ValueError:
        return JsonResponse({"error": "Invalid amount"}, status=400)

    try:
        # Call your helper function to trigger STK Push
        response = stk_push(phone, amount)
        return JsonResponse({"success": True, "response": response})
    except Exception as e:
        # Catch any errors and return them for debugging
        return JsonResponse({"success": False, "error": str(e)}, status=500)



@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body.decode("utf-8"))
    # Handle payment result here (save to DB, update order status)
    print("M-Pesa Callback:", data)

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Callback received successfully"})




