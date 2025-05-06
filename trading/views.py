from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import (
    BarterCredit, CreditTransaction, Listing, 
    TradeOffer, ShippingInfo, TradeCompletion
)
from artifacts.models import Artifact

@login_required
def marketplace(request):
    """View the marketplace with all active listings"""
    listings = Listing.objects.filter(status='active').select_related('seller', 'artifact')
    return render(request, 'trading/marketplace.html', {'listings': listings})

@login_required
def listing_list(request):
    """View all listings by the current user"""
    listings = Listing.objects.filter(seller=request.user)
    return render(request, 'trading/listing_list.html', {'listings': listings})

@login_required
def listing_create(request):
    """Create a new listing"""
    # Placeholder for listing creation logic
    return render(request, 'trading/listing_form.html')

@login_required
def listing_detail(request, pk):
    """View a specific listing"""
    listing = get_object_or_404(Listing, pk=pk)
    return render(request, 'trading/listing_detail.html', {'listing': listing})

@login_required
def listing_update(request, pk):
    """Update an existing listing"""
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    # Placeholder for listing update logic
    return render(request, 'trading/listing_form.html', {'listing': listing})

@login_required
def listing_delete(request, pk):
    """Delete a listing"""
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    # Placeholder for listing deletion logic
    return redirect('trading:listing_list')

@login_required
def make_offer(request, listing_id):
    """Make an offer on a listing"""
    listing = get_object_or_404(Listing, pk=listing_id, status='active')
    # Placeholder for offer creation logic
    return render(request, 'trading/make_offer.html', {'listing': listing})

@login_required
def offer_list(request):
    """View all offers (both sent and received)"""
    sent_offers = TradeOffer.objects.filter(buyer=request.user)
    received_offers = TradeOffer.objects.filter(listing__seller=request.user)
    return render(request, 'trading/offer_list.html', {
        'sent_offers': sent_offers,
        'received_offers': received_offers
    })

@login_required
def received_offers(request):
    """View offers received on your listings"""
    offers = TradeOffer.objects.filter(listing__seller=request.user)
    return render(request, 'trading/received_offers.html', {'offers': offers})

@login_required
def sent_offers(request):
    """View offers you've sent"""
    offers = TradeOffer.objects.filter(buyer=request.user)
    return render(request, 'trading/sent_offers.html', {'offers': offers})

@login_required
def offer_detail(request, pk):
    """View a specific offer"""
    offer = get_object_or_404(
        TradeOffer.objects.select_related('listing', 'buyer', 'listing__seller'),
        Q(buyer=request.user) | Q(listing__seller=request.user),
        pk=pk
    )
    return render(request, 'trading/offer_detail.html', {'offer': offer})

@login_required
def accept_offer(request, pk):
    """Accept a trade offer"""
    offer = get_object_or_404(TradeOffer, pk=pk, listing__seller=request.user, status='pending')
    # Placeholder for offer acceptance logic
    return redirect('trading:offer_detail', pk=offer.pk)

@login_required
def reject_offer(request, pk):
    """Reject a trade offer"""
    offer = get_object_or_404(TradeOffer, pk=pk, listing__seller=request.user, status='pending')
    # Placeholder for offer rejection logic
    return redirect('trading:offer_detail', pk=offer.pk)

@login_required
def cancel_offer(request, pk):
    """Cancel an offer you've sent"""
    offer = get_object_or_404(TradeOffer, pk=pk, buyer=request.user, status='pending')
    # Placeholder for offer cancellation logic
    return redirect('trading:offer_detail', pk=offer.pk)

@login_required
def shipping_address_list(request):
    """View all shipping addresses"""
    addresses = ShippingInfo.objects.filter(user=request.user)
    return render(request, 'trading/shipping_address_list.html', {'addresses': addresses})

@login_required
def shipping_address_create(request):
    """Create a new shipping address"""
    # Placeholder for address creation logic
    return render(request, 'trading/shipping_address_form.html')

@login_required
def shipping_address_update(request, pk):
    """Update an existing shipping address"""
    address = get_object_or_404(ShippingInfo, pk=pk, user=request.user)
    # Placeholder for address update logic
    return render(request, 'trading/shipping_address_form.html', {'address': address})

@login_required
def shipping_address_delete(request, pk):
    """Delete a shipping address"""
    address = get_object_or_404(ShippingInfo, pk=pk, user=request.user)
    # Placeholder for address deletion logic
    return redirect('trading:shipping_address_list')

@login_required
def set_default_shipping(request, pk):
    """Set a shipping address as default"""
    address = get_object_or_404(ShippingInfo, pk=pk, user=request.user)
    address.is_default = True
    address.save()  # The model's save method will handle making others non-default
    messages.success(request, "Default shipping address updated.")
    return redirect('trading:shipping_address_list')

@login_required
def complete_trade(request, pk):
    """Complete a trade after accepting an offer"""
    # First filter the queryset
    offers = TradeOffer.objects.filter(
        pk=pk,
        status='accepted'
    ).filter(
        Q(buyer=request.user) | Q(listing__seller=request.user)
    )
    # Then get the object
    offer = get_object_or_404(offers)
    # Placeholder for trade completion logic
    return redirect('trading:offer_detail', pk=offer.pk)

@login_required
def trade_shipping_info(request, pk):
    """View shipping info for a trade"""
    trade = get_object_or_404(
        TradeCompletion,
        Q(trade_offer__buyer=request.user) | Q(trade_offer__listing__seller=request.user),
        trade_offer_id=pk
    )
    return render(request, 'trading/trade_shipping_info.html', {'trade': trade})

@login_required
def update_tracking(request, pk):
    """Update tracking information for a trade"""
    trade = get_object_or_404(
        TradeCompletion,
        trade_offer__listing__seller=request.user,
        trade_offer_id=pk
    )
    # Placeholder for tracking update logic
    return redirect('trading:trade_shipping_info', pk=pk)

@login_required
def mark_shipped(request, pk):
    """Mark an item as shipped"""
    trade = get_object_or_404(
        TradeCompletion,
        trade_offer__listing__seller=request.user,
        trade_offer_id=pk
    )
    trade.seller_shipping_status = 'shipped'
    trade.save()
    messages.success(request, "Item marked as shipped.")
    return redirect('trading:trade_shipping_info', pk=pk)

@login_required
def mark_delivered(request, pk):
    """Mark an item as delivered"""
    trade = get_object_or_404(
        TradeCompletion,
        trade_offer__buyer=request.user,
        trade_offer_id=pk
    )
    trade.buyer_shipping_status = 'delivered'
    trade.save()
    messages.success(request, "Item marked as delivered.")
    return redirect('trading:trade_shipping_info', pk=pk)

@login_required
def leave_feedback(request, pk):
    """Leave feedback for a completed trade"""
    trade = get_object_or_404(
        TradeCompletion,
        Q(trade_offer__buyer=request.user) | Q(trade_offer__listing__seller=request.user),
        trade_offer_id=pk
    )
    # Placeholder for feedback logic
    return render(request, 'trading/leave_feedback.html', {'trade': trade})

@login_required
def barter_credits(request):
    """View barter credit balance and operations"""
    credit, created = BarterCredit.objects.get_or_create(user=request.user)
    return render(request, 'trading/barter_credits.html', {'credit': credit})

@login_required
def transaction_history(request):
    """View transaction history"""
    transactions = CreditTransaction.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    )
    return render(request, 'trading/transaction_history.html', {'transactions': transactions})

@login_required
def transfer_credits(request):
    """Transfer barter credits to another user"""
    # Placeholder for credit transfer logic
    return render(request, 'trading/transfer_credits.html')
