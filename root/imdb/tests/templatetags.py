from django.test import TestCase
from django.utils import timezone

from unittest.mock import Mock

from .. import defaults
from ..templatetags import imdb_specials as filters


class FiltersTestCase(TestCase):
    def setUp(self):
        self.mock_image_field = Mock(url='http://example.com/pic.png')
        self.mock_user_with_pic = type('User', (object,), {
            'profile': type('Profile', (object,), {
                'pic': self.mock_image_field,
            })()
        })()

    def test_duration_hm(self):
        td = timezone.timedelta(hours=1, minutes=30, seconds=15)
        result = filters.duration_hm(td)
        self.assertEqual(result, '1h 30m')

    def test_or_default_video_url(self):
        video_url = 'http://example.com/video.mp4'
        result = filters.or_default_video_url(video_url)
        self.assertEqual(result, video_url)

        video_url = ''
        result = filters.or_default_video_url(video_url)
        self.assertEqual(result, defaults.DEFAULT_VIDEO_URL)

    def test_movie_pic_url_or_default(self):
        result = filters.movie_pic_url_or_default(self.mock_image_field)
        self.assertEqual(result, self.mock_image_field.url)

        result = filters.movie_pic_url_or_default(None)
        self.assertEqual(result, defaults.DEFAULT_MOVIE_PIC_URL)

    def test_user_pic_url_or_default(self):
        result = filters.user_pic_url_or_default(self.mock_user_with_pic)
        self.assertEqual(result, self.mock_image_field.url)

        self.mock_user_with_pic.profile.pic = None
        result = filters.user_pic_url_or_default(self.mock_user_with_pic)
        self.assertEqual(result, defaults.DEFAULT_USER_PIC_URL)

    def test_director_pic_url_or_default(self):
        result = filters.director_pic_url_or_default(self.mock_image_field)
        self.assertEqual(result, self.mock_image_field.url)

        result = filters.director_pic_url_or_default(None)
        self.assertEqual(result, defaults.DEFAULT_DIRECTOR_PIC_URL)
