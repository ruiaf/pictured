from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from pictured.pictures.models import Picture
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from forms import ImageLoginForm

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

def identify(request):
    if not (request.method == 'POST' and request.FILES):
        return HttpResponseRedirect('/')

    picture_form = ImageLoginForm(request.POST, request.FILES)
    if picture_form.is_valid():
        picture=picture_form.save()
        request.session["new_pic"]=picture
        if request.user.is_authenticated():
            return HttpResponseRedirect('/me/')

        newuser_form = UserCreationForm();
        login_form = AuthenticationForm();
        return render_to_response('identify.html',
            {'pic': picture,
             'newuser_form': newuser_form,
             'login_form': login_form,
             },
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')


def show(request,username):
    #TODO: change the 404 to a proper error page
    user = get_object_or_404(User,username=username)
    if not request.user==user:
        #TODO: change this to a proper error page
        raise Http404
    if request.user.is_authenticated():
        pics = Picture.objects.filter(user=user).order_by('-creation_date')[:5]
    return render_to_response('user_main.html', {'user': user, 'pictures': pics})

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
