from django.views import generic

from .. import models


class DirectorList(generic.ListView):
    template_name = 'imdb/directors/index.html'
    queryset = models.Director.objects.all()
    context_object_name = 'directors'
    paginate_by = 10


class DirectorDetail(generic.DetailView):
    template_name = 'imdb/directors/detail.html'
    model = models.Director
    context_object_name = 'director'
