from django import forms

class BaseForm(forms.Form):
    """
    Base form class with common functionality and styling
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap-like classes to all form fields
        for field_name, field in self.fields.items():
            css_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css_classes} form-control'.strip()

class BaseModelForm(forms.ModelForm):
    """
    Base model form class with common functionality and styling
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap-like classes to all form fields
        for field_name, field in self.fields.items():
            css_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css_classes} form-control'.strip()
            
            # Add placeholder if not present
            if not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = field.label or field_name.title() 