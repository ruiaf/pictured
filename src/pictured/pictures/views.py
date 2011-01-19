from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from pictured.pictures.models import Picture
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.views.decorators.csrf import csrf_exempt
import random
from forms import ImageLoginForm
from hashlib import md5
import time

def take(request):
    image_form = ImageLoginForm()
    if not request.user.is_authenticated():
        login_form = AuthenticationForm();
    else:
        login_form=None
    return render_to_response('main.html',
            {'image_form': image_form,
             'login_form': login_form,
            },
            context_instance=RequestContext(request))

def show_picture(request,path):
    pic = get_object_or_404(Picture,picture=("pictures/"+path))
    return render_to_response('showpic.html',
            {'pic': pic, },
            context_instance=RequestContext(request))

def random_picture(request):
    number_of_records = Picture.objects.count()
    random_index = int(random.random()*number_of_records)+1
    random_pic = Picture.objects.get(pk = random_index)
    return render_to_response('showpic.html',
            {'pic': random_pic, },
            context_instance=RequestContext(request))

def redo_facerec(request,path):
    pic = get_object_or_404(Picture,picture=("pictures/"+path))
    pic.redo_facerec()
    return HttpResponseRedirect("/"+pic.picture.name)

def save_picture_form(request):
    if not (request.method == 'POST' and request.FILES):
        return HttpResponseRedirect('/')

    picture_form = ImageLoginForm(request.POST, request.FILES)
    return save_picture(request,picture_form)

@csrf_exempt
def save_picture_android(request):
    if not (request.method == 'POST' and request.FILES):
        return HttpResponse("/")

    img_name = md5(request.FILES["picture"].read()).hexdigest()
    print img_name
    request.FILES["picture"].seek(0)
    picture_file = SimpleUploadedFile("%s.jpg" % img_name, request.FILES["picture"].read(), "image/jpg")
    picture_form = ImageLoginForm(data={},files={'picture':picture_file})
    request.session.set_test_cookie()

    if picture_form.is_valid():
        picture=picture_form.save()
        return HttpResponse("/identify/%s/"%img_name)
    return HttpResponse("/")

@csrf_exempt
def save_picture_flash(request):
    if not (request.method == 'POST' and len(request.raw_post_data)<1024*1024):
        return HttpResponseRedirect('/')

    print "entrou"
    img_name = md5(request.raw_post_data).hexdigest()
    picture_file = SimpleUploadedFile("%s.png" % img_name, request.raw_post_data, "image/png")
    picture_form = ImageLoginForm(data={},files={'picture':picture_file})
    return save_picture(request,picture_form)

@csrf_exempt
def save_picture_jpg(request):
	if not (request.method == 'POST' and len(request.raw_post_data)<2048*2048):
		return HttpResponseRedirect('/')

	img_name = md5(request.raw_post_data).hexdigest()
	picture_file = SimpleUploadedFile("%s.jpg" % img_name, request.raw_post_data, "image/jpg")

	picture_form = ImageLoginForm(data={},files={'picture':picture_file})
	return save_picture(request,picture_form)

def save_picture(request,picture_form):
    print "a salvar"
    request.session.set_test_cookie()
    if picture_form.is_valid():
        print "valida"
        picture=picture_form.save()
        request.session["new_pic"]=picture
        if request.user.is_authenticated():
            return HttpResponseRedirect('/me/')
        else:
            return HttpResponseRedirect('/identify/')
    else:
        print "invalida"
        print picture_form
        return HttpResponseRedirect('/')

def identify(request,unique_code=None):
    if unique_code!=None:
        newpic = get_object_or_404(Picture,picture="pictures/%s.jpg"%unique_code)
        request.session["new_pic"]=newpic

    newuser_form = UserCreationForm();
    login_form = AuthenticationForm();
    request.session.set_test_cookie()
    return render_to_response('identify.html',
        {'pic': request.session["new_pic"],
            'newuser_form': newuser_form,
            'login_form': login_form,
    },
    context_instance=RequestContext(request))


def show(request,username):
    #TODO: change the 404 to a proper error page
    user = get_object_or_404(User,username=username)
    if not request.user==user:
        #TODO: change this to a proper error page
        raise Http404
    if request.user.is_authenticated():
        pics = Picture.objects.filter(user=user).order_by('-creation_date')
    return render_to_response('user_main.html', {'pictures': pics},
            context_instance=RequestContext(request))

def lookalike(request,username):
    #TODO: change the 404 to a proper error page
    user = get_object_or_404(User,username=username)
    if not request.user==user:
        #TODO: change this to a proper error page
        raise Http404
    if request.user.is_authenticated():
        pics = Picture.objects.all().order_by('-creation_date')[:50]
    return render_to_response('lookalike.html', {'pictures': pics},
            context_instance=RequestContext(request))

@login_required()
def me(request):
    if request.session.has_key("new_pic") and request.session["new_pic"]!=None:
        pic = request.session["new_pic"]
        pic.user = request.user
        pic.save()
        request.session["new_pic"]=None
    return HttpResponseRedirect('/users/'+request.user.username+'/')

#####
# Perhaps put these 2 in different files
#####

def picture_register(request):
    if request.method == 'POST':
        newuser_form = UserCreationForm(request.POST)
        if newuser_form.is_valid():
            new_user = newuser_form.save()
            user = authenticate(username=request.POST["username"],password=request.POST["password1"])
            login(request,user)
            return me(request)
        else:
            login_form = AuthenticationForm();
            return render_to_response('identify.html',
                {'pic': request.session["new_pic"],
                'newuser_form': newuser_form,
                'login_form': login_form,
                },
                context_instance=RequestContext(request))

    return HttpResponseRedirect("/")

def picture_login(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request,request.POST)
        if login_form.is_valid():
            user = authenticate(username=request.POST["username"],password=request.POST["password"])
            if user is not None:
                login(request,user)
                return me(request)

        newuser_form = UserCreationForm();
        return render_to_response('identify.html',
                {'pic': request.session["new_pic"],
                    'newuser_form': newuser_form,
                    'login_form': login_form,
                    },
                context_instance=RequestContext(request))

    return HttpResponseRedirect("/")
