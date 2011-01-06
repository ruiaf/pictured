from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from pictured.pictures.models import Picture
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from forms import ImageLoginForm

def take(request):
    if request.method == 'POST':
        if request.FILES:
            image_form = ImageLoginForm(request.POST, request.FILES)
            if image_form.is_valid():
                image_form.save()
                return HttpResponseRedirect('/users/ruiaf/')

        else:
            login_form = ImageLoginForm(request.POST)
            if login_form.is_valid():
                user = authenticate(username=request.POST['username'],
                        password=request.POST['password'])
                login(request, user)
                return HttpResponseRedirect('/users/ruiaf/')

        #TODO: error handeling
        raise Http404

    login_form = AuthenticationForm();
    image_form = ImageLoginForm()
    return render_to_response('main.html',
            {'image_form': image_form,
             'login_form': login_form },
            context_instance=RequestContext(request))

def show(request,username):
    #TODO: change the 404 to a proper error page
    user = get_object_or_404(User,username=username)
    if not request.user==user:
        #TODO: change this to a proper error page
        raise Http404
    if request.user.is_authenticated():
        pics = Picture.objects.filter(user=user).order_by('-creation_date')[:5]
    return render_to_response('user_main.html', {'user': user, 'pictures': pics})
