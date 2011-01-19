from django import forms
from pictures.models import Picture

class ImageLoginForm(forms.ModelForm):
    class Meta:
        model=Picture
        exclude=('thumbnail',
                    'square_thumbnail',
                    'face',
                    'nose',
                    'mouth',
                    'eyes',
                    'eyebrows',
                    'left_eye',
                    'right_eye',
                    'left_eyebrow',
                    'right_eyebrow',
                    'user',
                    )
