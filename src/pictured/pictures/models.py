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
    mouth = models.ImageField(upload_to='pictures',verbose_name='mouth',null=True)
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
        self.left_eye=None
        self.right_eye=None
        self.eyes=None
        self.nose=None
        self.mouth=None
        self.save()

    def save(self, *args, **kwargs):
        super(Picture, self).save(*args, **kwargs) # Call the "real" save() method.

        # face detection
        from django.core.files.storage import get_storage_class
        pic_location = str(settings.MEDIA_ROOT+self.picture.name)
        (face_pos,eyes_pos,nose_pos,mouth_pos,leye_pos,reye_pos) = self.detect_objects(pic_location);

        # generate images
        self.generate_thumbnail()
        self.generate_squarethumbnail()
        self.generate_face(face_pos)
        self.generate_eyes(eyes_pos)
        self.generate_nose(nose_pos)
        self.generate_mouth(mouth_pos)
        self.generate_leye(leye_pos)
        self.generate_reye(reye_pos)
        super(Picture, self).save(*args, **kwargs) # Call the "real" save() method.

    def crop_scale_and_save(self,image_object, crop_rec=None, final_size=None, filename_extension="def_png"):
            self.picture.seek(0)
            image = Image.open(self.picture)

            # Convert to RGB if necessary
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            print "------------>",crop_rec,final_size
            if crop_rec:
                image = image.crop(crop_rec)
            if final_size:
                image.thumbnail(final_size, Image.ANTIALIAS)

            # Save the thumbnail
            temp_handle = StringIO()
            image.save(temp_handle, 'png')
            temp_handle.seek(0)

            # Save to the thumbnail field
            suf = SimpleUploadedFile(os.path.basename(self.picture.name),
                temp_handle.read(),
                content_type='image/png')
            temp_handle.close()
            image_object.save(os.path.splitext(suf.name)[0]+filename_extension, suf, save=False)


    def generate_thumbnail(self):
         if not self.thumbnail:
             self.crop_scale_and_save(self.thumbnail,None,(128,128),"thumb.png")

    def generate_squarethumbnail(self):
         if not self.square_thumbnail:
            width, height = self.picture.width, self.picture.height

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

            self.crop_scale_and_save(self.square_thumbnail,(left,upper,right,lower),(128,128),"sq_thumb.png")

    def generate_face(self,face_position):
         if face_position==None:
            return
         if not self.face:
            self.crop_scale_and_save(self.face,face_position,None,"face.png")

    def generate_eyes(self,eyes_position):
         if eyes_position==None:
            return
         if not self.eyes:
            self.crop_scale_and_save(self.eyes,eyes_position,None,"eyes.png")

    def generate_mouth(self,mouth_position):
         if mouth_position==None:
            return
         if not self.mouth:
            self.crop_scale_and_save(self.mouth,mouth_position,None,"mouth.png")

    def generate_nose(self,nose_position):
         if nose_position==None:
            return
         if not self.nose:
            self.crop_scale_and_save(self.nose,nose_position,None,"nose.png")

    def generate_leye(self,leye_position):
         if leye_position==None:
            return
         if not self.left_eye:
            self.crop_scale_and_save(self.left_eye,leye_position,None,"leye.png")

    def generate_reye(self,reye_position):
         if reye_position==None:
            return
         if not self.right_eye:
            self.crop_scale_and_save(self.right_eye,reye_position,None,"reye.png")

    def detect_objects(self,image_path):
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
        face = None
        for i,f in enumerate(faces):
            size = f.width*f.height
            if size>max_size:
                max_size=size
                face=f
                best_pic = (f.x, f.y, f.x+f.width, f.y+f.height)

        best_left_eye=None
        best_right_eye=None
        best_eyes = None
        best_nose = None
        best_mouth = None

        if face:
            # eyes
            cvClearMemStorage(storage)
            cascade_e = cvLoadHaarClassifierCascade( settings.EYES_HAAR_FILE, cvSize(1,1))
            eyes = cvHaarDetectObjects(grayscale,cascade_e,storage,1.15, 3, 0, cvSize(44,10))

            max_size = 0
            for i,e in enumerate(eyes):
                size = e.width*e.height
                if size>max_size:
                    max_size=size
                    eyes=e
                    best_eyes = (e.x, e.y, e.x+e.width, e.y+e.height)

            # lefteye
            cvClearMemStorage(storage)
            cascade_le = cvLoadHaarClassifierCascade( settings.LEFTEYE_HAAR_FILE, cvSize(1,1))
            eyes = cvHaarDetectObjects(grayscale,cascade_le,storage,1.15, 3, 0, cvSize(18,12))

            max_size = 0
            for i,e in enumerate(eyes):
                size = e.width*e.height
                if size>max_size:
                    max_size=size
                    leye=e
                    best_left_eye = (e.x, e.y, e.x+e.width, e.y+e.height)

            # righteye
            cvClearMemStorage(storage)
            cascade_re = cvLoadHaarClassifierCascade( settings.RIGHTEYE_HAAR_FILE, cvSize(1,1))
            eyes = cvHaarDetectObjects(grayscale,cascade_re,storage,1.15, 3, 0, cvSize(18,12))

            max_size = 0
            for i,e in enumerate(eyes):
                size = e.width*e.height
                if size>max_size:
                    max_size=size
                    leye=e
                    best_right_eye = (e.x, e.y, e.x+e.width, e.y+e.height)

            # nose
            cvClearMemStorage(storage)
            cascade_n = cvLoadHaarClassifierCascade( settings.NOSE_HAAR_FILE, cvSize(1,1))
            noses = cvHaarDetectObjects(grayscale,cascade_n,storage,1.15, 3, 0, cvSize(18,15))

            max_size = 0
            for i,n in enumerate(noses):
                size = n.width*n.height
                if size>max_size:
                    max_size=size
                    nose=n
                    best_nose = (n.x, n.y, n.x+n.width, n.y+n.height)

            # mouth
            cvClearMemStorage(storage)
            cascade_m = cvLoadHaarClassifierCascade( settings.MOUTH_HAAR_FILE, cvSize(1,1))
            mouths = cvHaarDetectObjects(grayscale,cascade_m,storage,1.15, 3, 0, cvSize(25,15))

            max_size = 0
            for i,m in enumerate(mouths):
                size = m.width*m.height
                if size>max_size:
                    max_size=size
                    mouth=m
                    best_mouth = (m.x, m.y, m.x+m.width, m.y+m.height)

        return (best_pic,best_eyes,best_nose,best_mouth,best_left_eye,best_right_eye)
