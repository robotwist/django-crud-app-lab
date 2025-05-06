from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Conversation, Message, Notification

# Create your views here.

@login_required
def conversation_list(request):
    """Display list of all user conversations"""
    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, 'user_messages/conversation_list.html', {'conversations': conversations})

@login_required
def start_conversation(request):
    """Start a new conversation"""
    # Placeholder for conversation creation logic
    return render(request, 'user_messages/start_conversation.html')

@login_required
def conversation_detail(request, conversation_id):
    """View a conversation and its messages"""
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('messages', 'messages__sender'),
        id=conversation_id, 
        participants=request.user
    )
    return render(request, 'user_messages/conversation_detail.html', {'conversation': conversation})

@login_required
def send_message(request, conversation_id):
    """Send a message in a conversation"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    # Placeholder for message sending logic
    return redirect('messages:conversation_detail', conversation_id=conversation.id)

@login_required
def mark_message_read(request, conversation_id, message_id):
    """Mark a message as read"""
    message = get_object_or_404(
        Message, 
        id=message_id, 
        conversation_id=conversation_id, 
        conversation__participants=request.user
    )
    message.is_read = True
    message.save()
    return redirect('messages:conversation_detail', conversation_id=conversation_id)

@login_required
def notification_list(request):
    """View all notifications"""
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'user_messages/notification_list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('messages:notification_list')

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('messages:notification_list')
