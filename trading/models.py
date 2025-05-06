from django.db import models
from django.conf import settings
from artifacts.models import Artifact

class BarterCredit(models.Model):
    """Represents the barter currency in the system"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='barter_credit', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s balance: {self.balance}"

class CreditTransaction(models.Model):
    """Records movements of barter credits between users or system"""
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('sale', 'Sale Proceeds'),
        ('purchase', 'Purchase'),
        ('system', 'System Adjustment'),
    )
    
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='sent_transactions', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='received_transactions', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type}: {self.amount} ({self.created_at.strftime('%Y-%m-%d')})"
    
    class Meta:
        ordering = ['-created_at']

class Listing(models.Model):
    """An artifact listed for trade or sale"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('pending', 'Pending Transaction'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    LISTING_TYPES = (
        ('sale', 'For Sale'),
        ('trade', 'For Trade'),
        ('both', 'Sale or Trade'),
    )
    
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='listings', on_delete=models.CASCADE)
    artifact = models.ForeignKey(Artifact, related_name='listings', on_delete=models.CASCADE)
    listing_type = models.CharField(max_length=5, choices=LISTING_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    preferred_trades = models.TextField(blank=True, help_text="Describe what you're looking for in trades")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.artifact.title} ({self.get_listing_type_display()})"
    
    class Meta:
        ordering = ['-created_at']

class TradeOffer(models.Model):
    """An offer to trade or buy an artifact"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    listing = models.ForeignKey(Listing, related_name='offers', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='trade_offers', on_delete=models.CASCADE)
    offer_type = models.CharField(max_length=5, choices=Listing.LISTING_TYPES)
    offered_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    offered_artifacts = models.ManyToManyField(Artifact, related_name='trade_offers', blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Offer on {self.listing.artifact.title} by {self.buyer.username} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']

class ShippingInfo(models.Model):
    """Shipping information for completed trades"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='shipping_addresses', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}'s address in {self.city}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            ShippingInfo.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class TradeCompletion(models.Model):
    """Records the final details of a completed trade"""
    SHIPPING_STATUS = (
        ('pending', 'Pending Shipment'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )
    
    trade_offer = models.OneToOneField(TradeOffer, related_name='completion', on_delete=models.CASCADE)
    buyer_shipping = models.ForeignKey(
        ShippingInfo, 
        related_name='as_buyer_completions', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    seller_shipping = models.ForeignKey(
        ShippingInfo, 
        related_name='as_seller_completions', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    tracking_number = models.CharField(max_length=100, blank=True)
    buyer_shipping_status = models.CharField(max_length=10, choices=SHIPPING_STATUS, default='pending')
    seller_shipping_status = models.CharField(max_length=10, choices=SHIPPING_STATUS, default='pending')
    feedback_buyer = models.TextField(blank=True)
    feedback_seller = models.TextField(blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Completion of {self.trade_offer}"
