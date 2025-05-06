from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users that uses the CustomUser model."""
    email = forms.EmailField(required=True)
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text="Tell us about yourself"
    )
    website = forms.URLField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'bio', 'website', 'password1', 'password2') 