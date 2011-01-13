from django.db import models
from django.contrib.auth.models import User

from django.core.files import File
from cStringIO import StringIO
from PIL import Image
import glob, os

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

    def save(self, *args, **kwargs):
        self.generate_thumbnail()
        self.generate_squarethumbnail()
        super(Picture, self).save(*args, **kwargs) # Call the "real" save() method.

    def generate_thumbnail(self):
         if not self.thumbnail:
            # We use PIL's Image object
            # Docs: http://www.pythonware.com/library/pil/handbook/image.htm
            from PIL import Image
            from cStringIO import StringIO
            from django.core.files.uploadedfile import SimpleUploadedFile

            # Set our max thumbnail size in a tuple (max width, max height)
            THUMBNAIL_SIZE = (128, 128)

            # Open original photo which we want to thumbnail using PIL's Image
            # object
            self.picture.seek(0)
            image = Image.open(self.picture)

            # Convert to RGB if necessary
            # Thanks to Limodou on DjangoSnippets.org
            # http://www.djangosnippets.org/snippets/20/
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            # We use our PIL Image object to create the thumbnail, which already
            # has a thumbnail() convenience method that contrains proportions.
            # Additionally, we use Image.ANTIALIAS to make the image look better.
            # Without antialiasing the image pattern artifacts may result.
            image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

            # Save the thumbnail
            temp_handle = StringIO()
            image.save(temp_handle, 'png')
            temp_handle.seek(0)

            # Save to the thumbnail field
            suf = SimpleUploadedFile(os.path.split(self.picture.name)[-1],
            temp_handle.read(), content_type='image/png')
            self.thumbnail.save(suf.name+'_thumbnail.png', suf, save=False)

            image.save(self.thumbnail.name)
            temp_handle.close()

    def generate_squarethumbnail(self):
         if not self.square_thumbnail:
            # We use PIL's Image object
            # Docs: http://www.pythonware.com/library/pil/handbook/image.htm
            from PIL import Image
            from cStringIO import StringIO
            from django.core.files.uploadedfile import SimpleUploadedFile

            # Set our max thumbnail size in a tuple (max width, max height)
            THUMBNAIL_SIZE = (128, 128)

            # Open original photo which we want to thumbnail using PIL's Image
            # object
            self.picture.seek(0)
            image = Image.open(self.picture)

            # Convert to RGB if necessary
            # Thanks to Limodou on DjangoSnippets.org
            # http://www.djangosnippets.org/snippets/20/
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            # We use our PIL Image object to create the thumbnail, which already
            # has a thumbnail() convenience method that contrains proportions.
            # Additionally, we use Image.ANTIALIAS to make the image look better.
            # Without antialiasing the image pattern artifacts may result.
            width, height = image.size

            if width > height:
                delta = width - height
                left = int(delta/2)
                upper = 0
                right = height + left
                lower = height
            else:
                delta = height - width
                left = 0
                upper = int(delta/2)
                right = width
                lower = width + upper

            image = image.crop((left, upper, right, lower))
            image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

            # Save the thumbnail
            temp_handle = StringIO()
            image.save(temp_handle, 'png')
            temp_handle.seek(0)

            # Save to the thumbnail field
            suf = SimpleUploadedFile(os.path.split(self.picture.name)[-1],
            temp_handle.read(), content_type='image/png')
            self.square_thumbnail.save(suf.name+'_sqthumbnail.png', suf, save=False)
            image.save(self.square_thumbnail.name)

    def thumb(self):
        return "<img src=\"/media/"+str(self.square_thumbnail)+"\" / >"
