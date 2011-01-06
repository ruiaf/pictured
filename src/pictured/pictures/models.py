from django.db import models
from django.contrib.auth.models import User

class Picture(models.Model):
    mug_shot = models.ImageField(upload_to='pictures',verbose_name='picture')
    creation_date = models.DateTimeField(verbose_name='date taken',auto_now=True)
    user = models.ForeignKey(User,null=True)
