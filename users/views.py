from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import CustomUser, Friendship
from .forms import CustomUserCreationForm

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, f'Account created for {username}!')
            return redirect('artifact_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def user_profile(request):
    """Show the current user's profile"""
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    """Edit the current user's profile"""
    # Placeholder for profile editing logic
    return render(request, 'users/edit_profile.html')

@login_required
def view_profile(request, username):
    """View another user's profile"""
    user = get_object_or_404(CustomUser, username=username)
    # Check if they are friends
    is_friend = Friendship.are_friends(request.user, user)
    # Check if the user has sent a friend request
    is_pending = Friendship.objects.filter(
        sender=request.user, 
        receiver=user, 
        status='pending'
    ).exists()
    return render(request, 'users/view_profile.html', {
        'profile_user': user,
        'is_friend': is_friend,
        'is_pending': is_pending
    })

@login_required
def friend_list(request):
    """List the current user's friends"""
    friends_sent = Friendship.objects.filter(
        sender=request.user, 
        status='accepted'
    ).select_related('receiver')
    
    friends_received = Friendship.objects.filter(
        receiver=request.user, 
        status='accepted'
    ).select_related('sender')
    
    return render(request, 'users/friend_list.html', {
        'friends_sent': friends_sent,
        'friends_received': friends_received
    })

@login_required
def friend_requests(request):
    """View pending friend requests"""
    received_requests = Friendship.objects.filter(
        receiver=request.user, 
        status='pending'
    ).select_related('sender')
    
    sent_requests = Friendship.objects.filter(
        sender=request.user, 
        status='pending'
    ).select_related('receiver')
    
    return render(request, 'users/friend_requests.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests
    })

@login_required
def send_friend_request(request, username):
    """Send a friend request to another user"""
    other_user = get_object_or_404(CustomUser, username=username)
    
    # Can't send request to yourself
    if other_user == request.user:
        messages.error(request, "You can't send a friend request to yourself.")
        return redirect('users:view_profile', username=username)
    
    # Check if already friends
    if Friendship.are_friends(request.user, other_user):
        messages.info(request, f"You are already friends with {other_user.username}.")
        return redirect('users:view_profile', username=username)
    
    # Check if request already exists
    if Friendship.objects.filter(sender=request.user, receiver=other_user).exists():
        messages.info(request, f"You already sent a friend request to {other_user.username}.")
        return redirect('users:view_profile', username=username)
    
    # Create friend request
    Friendship.objects.create(sender=request.user, receiver=other_user, status='pending')
    messages.success(request, f"Friend request sent to {other_user.username}.")
    return redirect('users:view_profile', username=username)

@login_required
def accept_friend_request(request, request_id):
    """Accept a friend request"""
    friendship = get_object_or_404(Friendship, id=request_id, receiver=request.user, status='pending')
    friendship.status = 'accepted'
    friendship.save()
    messages.success(request, f"You are now friends with {friendship.sender.username}.")
    return redirect('users:friend_list')

@login_required
def reject_friend_request(request, request_id):
    """Reject a friend request"""
    friendship = get_object_or_404(Friendship, id=request_id, receiver=request.user, status='pending')
    friendship.status = 'rejected'
    friendship.save()
    messages.success(request, f"Friend request from {friendship.sender.username} rejected.")
    return redirect('users:friend_requests')

@login_required
def remove_friend(request, username):
    """Remove a user from friends"""
    other_user = get_object_or_404(CustomUser, username=username)
    
    # Remove friendship in either direction
    Friendship.objects.filter(
        (models.Q(sender=request.user, receiver=other_user) | 
         models.Q(sender=other_user, receiver=request.user)),
        status='accepted'
    ).delete()
    
    messages.success(request, f"{other_user.username} has been removed from your friends.")
    return redirect('users:friend_list')
