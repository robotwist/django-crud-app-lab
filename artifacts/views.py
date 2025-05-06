import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Artifact, Comment, Category, Tag, UserPreference
from .forms import ArtifactForm, CommentForm, ArtifactSearchForm, UserPreferenceForm

# Get the custom user model
User = get_user_model()

logger = logging.getLogger(__name__)

def get_filtered_artifacts(user, base_queryset):
    """Helper function to filter artifacts based on user preferences"""
    if not user.is_authenticated:
        return base_queryset
    
    try:
        preferences = user.preferences
        # Exclude artifacts from blocked users
        base_queryset = base_queryset.exclude(user__in=preferences.blocked_users.all())
        # Exclude artifacts with blocked tags
        base_queryset = base_queryset.exclude(tags__in=preferences.blocked_tags.all())
        # Exclude artifacts with blocked categories
        base_queryset = base_queryset.exclude(category__in=preferences.blocked_categories.all())
    except UserPreference.DoesNotExist:
        # If user has no preferences, create them
        UserPreference.objects.create(user=user)
    
    return base_queryset.distinct()

def render_artifact_list(request, artifacts):
    """Helper function to render artifact list items for both initial page load and AJAX"""
    context = {'artifacts': artifacts}
    return render_to_string('artifacts/includes/artifact_list_items.html', context, request=request)

@cache_page(60 * 15)  # Cache for 15 minutes
def artifact_list(request):
    form = ArtifactSearchForm(request.GET)
    artifacts = Artifact.objects.select_related('category', 'user').prefetch_related('tags')
    
    # Apply user preferences filtering
    artifacts = get_filtered_artifacts(request.user, artifacts)
    
    if form.is_valid():
        # Search by query
        query = form.cleaned_data.get('q')
        if query:
            artifacts = artifacts.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        # Filter by category
        category = form.cleaned_data.get('category')
        if category:
            artifacts = artifacts.filter(category=category)
        
        # Sort - always prioritize chronological order
        sort_by = form.cleaned_data.get('sort')
        if sort_by:
            artifacts = artifacts.order_by(sort_by)
        else:
            artifacts = artifacts.order_by('-created_at')
    else:
        # Default sorting is chronological
        artifacts = artifacts.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(artifacts, settings.INFINITE_SCROLL_BATCH_SIZE)
    page = request.GET.get('page', 1)
    artifacts = paginator.get_page(page)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        has_next = artifacts.has_next()
        html = render_artifact_list(request, artifacts)
        return JsonResponse({
            'html': html,
            'has_next': has_next,
            'next_page': artifacts.next_page_number() if has_next else None,
        })
    
    context = {
        'artifacts': artifacts,
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'artifacts/artifact_list.html', context)

@login_required
def artifact_detail(request, pk):
    artifact = get_object_or_404(
        Artifact.objects.select_related('category', 'user').prefetch_related('tags', 'comments__user'),
        pk=pk
    )
    
    # Check if artifact should be visible to user
    if artifact not in get_filtered_artifacts(request.user, Artifact.objects.filter(pk=artifact.pk)):
        messages.error(request, "This content has been filtered based on your preferences.")
        return redirect('artifact_list')
    
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.artifact = artifact
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('artifact_detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'artifact': artifact,
        'comment_form': comment_form,
    }
    return render(request, 'artifacts/artifact_detail.html', context)

@login_required
def artifact_create(request):
    if request.method == "POST":
        form = ArtifactForm(request.POST, request.FILES)
        if form.is_valid():
            artifact = form.save(commit=False)
            artifact.user = request.user
            artifact.save()
            form.save_m2m()  # Save tags
            messages.success(request, 'Artifact created successfully!')
            logger.info(f'New artifact created: {artifact.title} by {request.user.username}')
            return redirect('artifact_detail', pk=artifact.pk)
    else:
        form = ArtifactForm()
    return render(request, 'artifacts/artifact_form.html', {'form': form})

@login_required
def artifact_update(request, pk):
    artifact = get_object_or_404(Artifact, pk=pk)
    
    # Only allow the owner to update
    if artifact.user != request.user:
        messages.error(request, "You don't have permission to edit this artifact.")
        return redirect('artifact_detail', pk=pk)
    
    if request.method == "POST":
        form = ArtifactForm(request.POST, request.FILES, instance=artifact)
        if form.is_valid():
            artifact = form.save()
            messages.success(request, 'Artifact updated successfully!')
            logger.info(f'Artifact updated: {artifact.title} by {request.user.username}')
            return redirect('artifact_detail', pk=artifact.pk)
    else:
        form = ArtifactForm(instance=artifact)
    return render(request, 'artifacts/artifact_form.html', {'form': form})

@login_required
def artifact_delete(request, pk):
    artifact = get_object_or_404(Artifact, pk=pk)
    
    # Only allow the owner to delete
    if artifact.user != request.user:
        messages.error(request, "You don't have permission to delete this artifact.")
        return redirect('artifact_detail', pk=pk)
    
    if request.method == "POST":
        title = artifact.title
        artifact.delete()
        messages.success(request, 'Artifact deleted successfully!')
        logger.info(f'Artifact deleted: {title} by {request.user.username}')
        return redirect('artifact_list')
    return render(request, 'artifacts/artifact_confirm_delete.html', {'artifact': artifact})

@login_required
@require_POST
def artifact_like(request, pk):
    artifact = get_object_or_404(Artifact, pk=pk)
    artifact.popularity_score += 1
    artifact.save()
    messages.success(request, 'Thanks for liking this artifact!')
    logger.info(f'Artifact liked: {artifact.title} by {request.user.username}')
    return redirect('artifact_detail', pk=pk)

@login_required
def user_feed(request):
    """Personal feed showing only artifacts from non-blocked users in chronological order"""
    artifacts = Artifact.objects.select_related('category', 'user').prefetch_related('tags')
    artifacts = get_filtered_artifacts(request.user, artifacts).order_by('-created_at')
    
    paginator = Paginator(artifacts, settings.ARTIFACTS_PER_PAGE)
    page = request.GET.get('page')
    artifacts = paginator.get_page(page)
    
    context = {
        'artifacts': artifacts,
        'feed_type': 'personal',
    }
    return render(request, 'artifacts/user_feed.html', context)

@login_required
def user_profile(request, username):
    """View for user profiles"""
    profile_user = get_object_or_404(User, username=username)
    artifacts = get_filtered_artifacts(request.user, profile_user.artifacts.all())
    
    # Get or create preferences for both users
    viewer_prefs, _ = UserPreference.objects.get_or_create(user=request.user)
    profile_prefs, _ = UserPreference.objects.get_or_create(user=profile_user)
    
    context = {
        'profile_user': profile_user,
        'preferences': profile_prefs,
        'artifacts': artifacts.order_by('-created_at'),
        'is_following': viewer_prefs.is_following(profile_user),
        'is_blocking': viewer_prefs.is_blocking(profile_user),
        'followers_count': profile_user.followers.count(),
        'following_count': profile_prefs.following.count(),
        'artifacts_count': artifacts.count(),
    }
    return render(request, 'artifacts/user_profile.html', context)

@login_required
def user_preferences(request):
    """View for user preferences page"""
    preferences, created = UserPreference.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = UserPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences updated successfully!')
            return redirect('user_preferences')
    else:
        form = UserPreferenceForm(instance=preferences)
    
    context = {
        'form': form,
        'preferences': preferences,
        'following_count': preferences.following.count(),
        'followers_count': request.user.followers.count(),
        'blocked_count': preferences.blocked_users.count(),
    }
    return render(request, 'artifacts/user_preferences.html', context)

@login_required
@require_POST
def follow_user(request, username):
    """Follow a user"""
    user_to_follow = get_object_or_404(User, username=username)
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)
    
    if user_to_follow != request.user:
        preferences.follow(user_to_follow)
        messages.success(request, f'You are now following {username}')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'following': True,
            'followers_count': user_to_follow.followers.count()
        })
    return redirect('user_profile', username=username)

@login_required
@require_POST
def unfollow_user(request, username):
    """Unfollow a user"""
    user_to_unfollow = get_object_or_404(User, username=username)
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)
    preferences.unfollow(user_to_unfollow)
    messages.success(request, f'You have unfollowed {username}')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'following': False,
            'followers_count': user_to_unfollow.followers.count()
        })
    return redirect('user_profile', username=username)

@login_required
@require_POST
def block_user(request, username):
    """Block a user"""
    user_to_block = get_object_or_404(User, username=username)
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)
    
    if user_to_block != request.user:
        preferences.block(user_to_block)
        messages.success(request, f'You have blocked {username}')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'blocked': True})
    return redirect('user_preferences')

@login_required
@require_POST
def unblock_user(request, username):
    """Unblock a user"""
    user_to_unblock = get_object_or_404(User, username=username)
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)
    preferences.unblock(user_to_unblock)
    messages.success(request, f'You have unblocked {username}')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'blocked': False})
    return redirect('user_preferences')
