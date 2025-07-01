from urllib.parse import urlparse

from django.contrib import auth
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.views import generic

from .util.generics import RedirectBackView
from ..redirect import get_redirect_or_referer


class Logout(RedirectBackView):
    def action(self, *args, **kwargs):
        auth.logout(self.request)


class Login(generic.TemplateView):
    template_name = 'imdb/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        referer = get_redirect_or_referer(self.request)
        context['redirect_to'] = urlparse(referer).path
        return context


def login_simple_api(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if user := auth.authenticate(request, username=username, password=password):
        auth.login(request, user)
        return HttpResponse('Successfully signed in', status=200)
    else:
        return HttpResponse('Unauthorized', status=401)


def register_simple_api(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    try:
        user = User.objects.create_user(username=username, password=password)
        auth.login(request, user)
        return HttpResponse('Successfully registered', status=201)
    except IntegrityError:
        return HttpResponse('Username already taken', status=409)
