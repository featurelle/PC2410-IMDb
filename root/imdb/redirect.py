def get_redirect_or_referer(request):
    return request.GET.get('redirect_to') or request.META.get('HTTP_REFERER')
