from django import forms
from .models import Artifact, Comment, Category, Tag, UserPreference
from core.forms import BaseModelForm, BaseForm

class ArtifactForm(BaseModelForm):
    tags = forms.CharField(required=False, help_text='Enter tags separated by commas')
    
    class Meta:
        model = Artifact
        fields = ['title', 'description', 'image', 'category', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['tags'] = ', '.join(tag.name for tag in self.instance.tags.all())
    
    def save(self, commit=True):
        artifact = super().save(commit=False)
        if commit:
            artifact.save()
            # Handle tags
            tag_names = [name.strip() for name in self.cleaned_data['tags'].split(',') if name.strip()]
            artifact.tags.clear()
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
                artifact.tags.add(tag)
        return artifact

class CommentForm(BaseModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }

class ArtifactSearchForm(BaseForm):
    q = forms.CharField(required=False, label='Search')
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    sort = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('-popularity_score', 'Most Popular'),
            ('title', 'Title A-Z'),
            ('-title', 'Title Z-A'),
        ],
        required=False,
        initial='-created_at'
    )

class UserPreferenceForm(BaseModelForm):
    class Meta:
        model = UserPreference
        fields = ['bio', 'website', 'blocked_tags', 'blocked_categories']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell others about yourself...'
            }),
            'website': forms.URLInput(attrs={
                'placeholder': 'https://your-website.com'
            }),
            'blocked_tags': forms.SelectMultiple(attrs={
                'class': 'select2',
                'data-placeholder': 'Select tags to block...'
            }),
            'blocked_categories': forms.SelectMultiple(attrs={
                'class': 'select2',
                'data-placeholder': 'Select categories to block...'
            })
        }
        help_texts = {
            'blocked_tags': 'Select tags whose content you don\'t want to see',
            'blocked_categories': 'Select categories whose content you don\'t want to see'
        }
