from django.urls import path
from . import views

app_name = 'trading'

urlpatterns = [
    # Marketplace
    path('marketplace/', views.marketplace, name='marketplace'),
    
    # Listings
    path('listings/', views.listing_list, name='listing_list'),
    path('listings/create/', views.listing_create, name='listing_create'),
    path('listings/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listings/<int:pk>/update/', views.listing_update, name='listing_update'),
    path('listings/<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    
    # Trade offers
    path('listings/<int:listing_id>/make-offer/', views.make_offer, name='make_offer'),
    path('offers/', views.offer_list, name='offer_list'),
    path('offers/received/', views.received_offers, name='received_offers'),
    path('offers/sent/', views.sent_offers, name='sent_offers'),
    path('offers/<int:pk>/', views.offer_detail, name='offer_detail'),
    path('offers/<int:pk>/accept/', views.accept_offer, name='accept_offer'),
    path('offers/<int:pk>/reject/', views.reject_offer, name='reject_offer'),
    path('offers/<int:pk>/cancel/', views.cancel_offer, name='cancel_offer'),
    
    # Shipping
    path('shipping-addresses/', views.shipping_address_list, name='shipping_address_list'),
    path('shipping-addresses/create/', views.shipping_address_create, name='shipping_address_create'),
    path('shipping-addresses/<int:pk>/update/', views.shipping_address_update, name='shipping_address_update'),
    path('shipping-addresses/<int:pk>/delete/', views.shipping_address_delete, name='shipping_address_delete'),
    path('shipping-addresses/<int:pk>/set-default/', views.set_default_shipping, name='set_default_shipping'),
    
    # Trade completion
    path('offers/<int:pk>/complete/', views.complete_trade, name='complete_trade'),
    path('trades/<int:pk>/shipping-info/', views.trade_shipping_info, name='trade_shipping_info'),
    path('trades/<int:pk>/update-tracking/', views.update_tracking, name='update_tracking'),
    path('trades/<int:pk>/mark-shipped/', views.mark_shipped, name='mark_shipped'),
    path('trades/<int:pk>/mark-delivered/', views.mark_delivered, name='mark_delivered'),
    path('trades/<int:pk>/feedback/', views.leave_feedback, name='leave_feedback'),
    
    # Barter credits
    path('barter-credits/', views.barter_credits, name='barter_credits'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transfer-credits/', views.transfer_credits, name='transfer_credits'),
] 