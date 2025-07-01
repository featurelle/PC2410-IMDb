from django.views import generic


class RedirectBackView(generic.RedirectView):
    def action(self, *args, **kwargs):
        pass

    def get_redirect_url(self, *args, **kwargs):
        self.action(*args, **kwargs)
        return self.request.META.get('HTTP_REFERER')
