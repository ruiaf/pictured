from django.http import HttpResponse
from django.shortcuts import render_to_response
from pictured.pictures.models import Picture

def take(request):
    return render_to_response('main.html')

def show(request,username):
    pics = Picture.objects.all().order_by('-creation_date')[:5]
    return render_to_response('user_main.html', {'user': username, 'pictures': pics})
