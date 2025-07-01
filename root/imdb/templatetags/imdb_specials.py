from django import template

from .. import defaults

register = template.Library()


@register.filter
def duration_hm(td):
    if td:
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f'{hours}h {minutes:>02}m'


@register.filter
def or_default_video_url(video_url):
    return video_url or defaults.DEFAULT_VIDEO_URL


@register.filter
def movie_pic_url_or_default(pic):
    return pic.url if pic else defaults.DEFAULT_MOVIE_PIC_URL


@register.filter
def user_pic_url_or_default(user):
    if hasattr(user, 'profile') and (pic := user.profile.pic):
        return pic.url
    else:
        return defaults.DEFAULT_USER_PIC_URL


@register.filter
def director_pic_url_or_default(pic):
    return pic.url if pic else defaults.DEFAULT_DIRECTOR_PIC_URL
