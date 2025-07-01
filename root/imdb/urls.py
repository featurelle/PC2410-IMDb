from django.apps import apps
from django.urls import path, include

from . import views

app_name = apps.get_app_config('imdb').name

urlpatterns = [

    path('', view=views.Index.as_view(), name='index'),
    path('search/', view=views.Search.as_view(), name='search'),
    path('movies/', include([
        path('', view=views.MovieList.as_view(), name='movies'),
        path('<int:pk>', view=views.MovieDetail.as_view(), name='movie_pk'),
        path('<slug:slug>', view=views.MovieDetail.as_view(), name='movie'),
        path('<int:pk>/ratings/post', view=views.RateMovie.as_view(), name='rate-movie'),
    ])),
    path('directors/', include([
        path('', view=views.DirectorList.as_view(), name='directors'),
        path('<int:pk>', view=views.DirectorDetail.as_view(), name='director_pk'),
        path('<slug:slug>', view=views.DirectorDetail.as_view(), name='director'),
    ])),
    path('auth/', include([
        path('login/', view=views.Login.as_view(), name='login-page'),
        path('logout/', view=views.Logout.as_view(), name='logout'),
    ])),
    path('user/', include([
        path('profile/', view=views.Profile.as_view(), name='profile'),
        path('watchlist/', view=views.Watchlist.as_view(), name='watchlist'),
        path('watchlist/<int:pk>/toggle', view=views.WatchlistToggle.as_view(), name='toggle-watchlist'),
        path('history/movies/', view=views.MovieHistory.as_view(), name='movies-viewed'),
    ])),
    path('api/', include([
        path('simple/', include([
            path('auth/login/', view=views.login_simple_api, name='login-api'),
            path('auth/register/', view=views.register_simple_api, name='register-api'),
        ])),
        path('rest/', include([
            path('movies/<int:pk>/comments/', view=views.MovieCommentRestAPI.as_view(), name='comments-api'),
        ])),
    ])),
]
