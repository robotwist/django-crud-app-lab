from django import forms
from .models import Artifact

class ArtifactForm(forms.ModelForm):
    class Meta:
        model = Artifact
        fields = ['title', 'description']
