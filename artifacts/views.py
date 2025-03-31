from django.shortcuts import render, get_object_or_404, redirect
from .models import Artifact
from .forms import ArtifactForm  # We'll make this next!
from django.views.decorators.http import require_POST

def artifact_list(request):
    artifacts = Artifact.objects.all()
    return render(request, 'artifacts/artifact_list.html', {'artifacts': artifacts})

def artifact_detail(request, pk):
    artifact = get_object_or_404(Artifact, pk=pk)
    return render(request, 'artifacts/artifact_detail.html', {'artifact': artifact})

def artifact_create(request):
    if request.method == "POST":
        form = ArtifactForm(request.POST)
        if form.is_valid():
            artifact = form.save()
            return redirect('artifact_detail', pk=artifact.pk)
    else:
        form = ArtifactForm()
    return render(request, 'artifacts/artifact_form.html', {'form': form})

def artifact_update(request, pk):
    artifact = get_object_or_404(Artifact, pk=pk)
    if request.method == "POST":
        form = ArtifactForm(request.POST, instance=artifact)
        if form.is_valid():
            artifact = form.save()
            return redirect('artifact_detail', pk=artifact.pk)
    else:
        form = ArtifactForm(instance=artifact)
    return render(request, 'artifacts/artifact_form.html', {'form': form})

def artifact_delete(request, pk):
    artifact = get_object_or_404(Artifact, pk=pk)
    if request.method == "POST":
        artifact.delete()
        return redirect('artifact_list')
    return render(request, 'artifacts/artifact_confirm_delete.html', {'artifact': artifact})


@require_POST
def artifact_like(request, pk):
    artifact = get_object_or_404(Artifact, pk=pk)
    artifact.popularity_score += 1
    artifact.save()
    return redirect('artifact_detail', pk=pk)
