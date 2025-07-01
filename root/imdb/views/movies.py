from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from django.http import Http404, HttpResponseNotFound

from django.views import generic
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .. import models, serializers
from .util.generics import RedirectBackView


class MovieList(generic.ListView):
    template_name = 'imdb/movies/index.html'
    queryset = models.Movie.objects.prefetch_related('ratings')
    context_object_name = 'movies'
    paginate_by = 10


class MovieDetail(generic.DetailView):
    middleware_classes = [SessionMiddleware]
    template_name = 'imdb/movies/detail.html'
    queryset = models.Movie.objects.prefetch_related(
        Prefetch(
            'comments',
            queryset=models.MovieComment.objects.prefetch_related('user').order_by('-timestamp')
        ),
        'ratings'
    )
    context_object_name = 'movie'

    def get(self, request, *args, **kwargs):
        try:
            movie = self.get_object()
        except Http404:
            return HttpResponseNotFound('<h1>Movie not found</h1>')

        session_key = request.session.session_key
        user = request.user if request.user.is_authenticated else None

        if session_key is None:
            request.session.save()
            session_key = request.session.session_key

        # Check if a MovieView instance already exists for this user or anon session
        if user:
            existing_view = models.MovieView.objects.filter(user=user, movie=movie).first()
        else:
            existing_view = models.MovieView.objects.filter(session_key=session_key, movie=movie).first()

        if not existing_view:
            # If not, create a new MovieView instance
            models.MovieView.objects.create(user=user, movie=movie, session_key=session_key)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = {
            'user_rating': None
        }
        try:
            extra_context['user_rating'] = context.get('movie').ratings.get(user=self.request.user).score
        except ObjectDoesNotExist:
            pass
        finally:
            return context | extra_context


class MovieCommentRestAPI(generics.ListCreateAPIView):
    serializer_class = serializers.MovieCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        prefetch_user = Prefetch('user', queryset=User.objects.prefetch_related('profile'))
        return models.MovieComment.objects.prefetch_related(prefetch_user).filter(
            movie__id=self.kwargs.get('pk')
        ).order_by('-timestamp')

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id') or request.user.id
        movie_id = request.data.get('movie_id') or kwargs.get('pk')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User with given ID does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            models.Movie.objects.get(id=movie_id)
        except models.Movie.DoesNotExist:
            return Response({'error': 'Movie with given ID does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, movie_id=movie_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RateMovie(RedirectBackView):
    def action(self, *args, **kwargs):
        user = self.request.user
        movie_pk = kwargs.get('pk')
        score = self.request.POST.get('rating')
        try:
            user_rating = user.ratings.get(movie__pk=movie_pk)
            user_rating.score = score
            user_rating.save()
        except ObjectDoesNotExist:
            movie = models.Movie.objects.get(pk=movie_pk)
            models.MovieRatingScore.objects.create(user=user, movie=movie, score=score)


# def rate_movie_simple_api(request):
#     user = request.user
#     movie_pk = request.POST.get('movie-id')
#     score = request.POST.get('rating')
#     try:
#         user_rating = user.ratings.get(movie__pk=movie_pk)
#         user_rating.score = score
#         user_rating.save()
#     except ObjectDoesNotExist:
#         movie = models.Movie.objects.get(pk=movie_pk)
#         models.MovieRatingScore.objects.create(user=user, movie=movie, score=score)
#     return HttpResponse(status=200)
