from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views import generic

from .. import models, forms
from .util.generics import RedirectBackView


class Watchlist(LoginRequiredMixin, generic.ListView):
    template_name = 'imdb/movies/watchlist.html'
    context_object_name = 'movies'
    paginate_by = 10
    login_url = reverse_lazy('imdb:login-page')
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        return self.request.user.watchlist.movies()


class MovieHistory(LoginRequiredMixin, generic.ListView):
    template_name = 'imdb/movies/viewed.html'
    context_object_name = 'movies'
    paginate_by = 10
    login_url = reverse_lazy('imdb:login-page')
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        return self.request.user.views.movies()


class WatchlistToggle(RedirectBackView):
    def action(self, *args, **kwargs):
        user = self.request.user
        movie = models.Movie.objects.get(pk=kwargs.get('pk'))
        if movie in user.watchlist.movies():
            user.watchlist.filter(movie=movie).delete()
        else:
            models.WatchlistEntry.objects.create(user=user, movie=movie)


class Profile(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = forms.UserAndProfileForm
    template_name = 'imdb/profile.html'
    login_url = reverse_lazy('imdb:login-page')
    redirect_field_name = 'redirect_to'

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def get_object(self, queryset=None):
        user = self.request.user
        try:
            user.profile
        except models.UserProfile.DoesNotExist:
            user.profile = models.UserProfile.objects.create(user=user)
        return user

    def form_valid(self, form):
        response = super().form_valid(form)
        # authenticate user with new password if password was changed
        new_password = form.cleaned_data.get('new_password2')
        if new_password:
            authenticated_user = auth.authenticate(
                request=self.request,
                username=self.request.user.username,
                password=new_password
            )
            if authenticated_user is not None:
                # login the authenticated user
                auth.login(self.request, authenticated_user)
        return response
