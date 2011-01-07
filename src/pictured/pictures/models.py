from django.db import models
from django.contrib.auth.models import User

class Picture(models.Model):
    picture = models.ImageField(upload_to='pictures',verbose_name='picture')
    thumbnail = models.ImageField(upload_to='pictures',verbose_name='thumbnail',null=True)
    square_thumbnail = models.ImageField(upload_to='pictures',verbose_name='square thumbnail',null=True)
    creation_date = models.DateTimeField(verbose_name='date taken',auto_now=True)

    face = models.ImageField(upload_to='pictures',verbose_name='face',null=True)
    nose = models.ImageField(upload_to='pictures',verbose_name='nose',null=True)
    eyes = models.ImageField(upload_to='pictures',verbose_name='eyes',null=True)
    eyebrows = models.ImageField(upload_to='pictures',verbose_name='eyebrows',null=True)

    left_eye = models.ImageField(upload_to='pictures',verbose_name='left eye',null=True)
    right_eye = models.ImageField(upload_to='pictures',verbose_name='right eye',null=True)
    left_eyebrow = models.ImageField(upload_to='pictures',verbose_name='left eyebrow',null=True)
    right_eyebrow = models.ImageField(upload_to='pictures',verbose_name='right eyebrow',null=True)

    user = models.ForeignKey(User,null=True)
