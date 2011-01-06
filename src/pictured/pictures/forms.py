from django import forms
from pictures.models import Picture

class ImageLoginForm(forms.ModelForm):
    class Meta:
        model=Picture
        #exclude=('user')
