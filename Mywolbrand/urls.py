from django.conf import settings
from django.contrib import admin
from django.urls import path
from . import views   


urlpatterns = [
    
    path("", views.homepage, name="homepage"),
    path("index", views.index, name="index"),

    path("register/", views.register, name="register"),

    path("login/", views.login, name="login"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path('contactus/', views.contactus, name='contactus'),

    path("logout/", views.logout_view, name="logout"),

    path("myprofile/", views.myprofile, name="myprofile"),

    path("sell/", views.sell,name="sell"),

    path("become-a-partner/", views.become_partner, name="become_partner"),

    path('request_contact/<int:item_id>/', views.request_contact, name='request_contact'),

    path("property_development/", views.property_development, name="property_development"),

    path("investment_education/", views.investment_education, name="investment_education"),

    path("privacy_policy/", views.privacy_policy, name="privacy_policy"),

    path("terms_of_service/", views.terms_of_service, name="terms_of_service"),
    
    path("interior_fitting/", views.interior_fitting, name="interior_fitting"),

    path("property/<int:pk>/", views.property_detail, name="property_detail"),

    path("my_bids/", views.my_bids, name="my_bids"),
    path("bid/add/<int:property_id>/", views.place_bid, name='place_bid'),
   
    path("my_cart/", views.my_cart, name="my_cart"),
    path("cart/add/<int:property_id>/", views.add_to_cart, name="add_to_cart"),

    path("faq/", views.faq, name="faq"),

    path('crypto-pay/', views.create_crypto_payment, name='create_crypto_payment'),
    path('coinbase-webhook/', views.coinbase_webhook, name='coinbase_webhook'),

    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path("callback/", views.mpesa_callback, name="mpesa_callback"),
    
]







