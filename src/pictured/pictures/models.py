from django.db import models
from django.contrib.auth.models import User

from django.core.files import File
from cStringIO import StringIO
from PIL import Image
import glob, os
from django.core.files.uploadedfile import SimpleUploadedFile
import settings


import sys, os
from opencv.cv import *
from opencv.highgui import *


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

    def redo_facerec(self):
        self.thumbnail=None
        self.square_thumbnail=None
        self.face=None
        self.save()

    def save(self, *args, **kwargs):
        super(Picture, self).save(*args, **kwargs) # Call the "real" save() method.
        self.generate_thumbnail()
        self.generate_squarethumbnail()
        self.generate_face()
        super(Picture, self).save(*args, **kwargs) # Call the "real" save() method.

    def generate_thumbnail(self):
         if not self.thumbnail:
            # We use PIL's Image object
            # Docs: http://www.pythonware.com/library/pil/handbook/image.htm

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
            suf = SimpleUploadedFile(os.path.basename(self.picture.name),
                temp_handle.read(),
                content_type='image/png')
            temp_handle.close()
            self.thumbnail.save(os.path.splitext(suf.name)[0]+'_thumbnail.png', suf, save=False)


    def generate_squarethumbnail(self):
         if not self.square_thumbnail:
            # We use PIL's Image object
            # Docs: http://www.pythonware.com/library/pil/handbook/image.htm
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
            suf = SimpleUploadedFile(os.path.basename(self.picture.name),
                temp_handle.read(), content_type='image/png')
            temp_handle.close()
            self.square_thumbnail.save(os.path.splitext(suf.name)[0]+'_sqthumbnail.png', suf, save=False)

    def generate_face(self):
         if not self.face:
            self.picture.seek(0)
            image = Image.open(self.picture)

            # Convert to RGB if necessary
            # Thanks to Limodou on DjangoSnippets.org
            # http://www.djangosnippets.org/snippets/20/
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            from django.core.files.storage import get_storage_class
            pic_location = str(settings.MEDIA_ROOT+self.picture.name)
            print pic_location
            face_position = self.detect_faces(pic_location);
            if face_position==None:
                return

            image = image.crop(face_position)

            # Save the thumbnail
            temp_handle = StringIO()
            image.save(temp_handle, 'png')
            temp_handle.seek(0)

            # Save to the thumbnail field
            suf = SimpleUploadedFile(os.path.basename(self.picture.name),
                temp_handle.read(), content_type='image/png')
            temp_handle.close()
            self.face.save(os.path.splitext(suf.name)[0]+'_face.png', suf, save=False)

    def detect_faces(self,image_path):
        """Converts an image to grayscale and returns the location of a face found"""
        print image_path
        image = cvLoadImage(image_path);

        if not image:
            return None

        grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
        cvCvtColor(image, grayscale, CV_BGR2GRAY)
        storage = cvCreateMemStorage(0)
        cvClearMemStorage(storage)
        cvEqualizeHist(grayscale, grayscale)
        cascade = cvLoadHaarClassifierCascade(
                settings.FACE_HAAR_FILE,
                cvSize(1,1))
        faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.2, 2,CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))

        max_size = 0
        best_pic = None
        for f in faces:
            size = f.width*f.height
            if size>max_size:
                max_size=size
                best_pic = (f.x, f.y, f.x+f.width, f.y+f.height)
        return best_pic
