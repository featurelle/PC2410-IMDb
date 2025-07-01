from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..models import UserProfile, Movie, Director


class ClearMediaSignalTestCase(TestCase):
    def setUp(self):
        self.pic_name = "django_signal_test_pic.jpg"
        self.pic = SimpleUploadedFile(
            self.pic_name,
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04"
            b"\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/jpeg"
        )

    def _test_pic_cleared(self, instance, pic):
        # Ensure the file exists before deletion
        pic_path = None
        try:
            pic_path = pic.path
        except ValueError:
            pass
        finally:
            self.assertIsNotNone(pic_path)
            self.assertTrue(default_storage.exists(pic_path))

        # Delete the User instance and the file
        instance.delete()

        # Ensure the file was deleted
        with self.assertRaises(FileNotFoundError):
            default_storage.open(pic_path)

    def test_user_pic_cleared(self):
        user = User.objects.create(username='testuser')
        UserProfile.objects.create(user=user, pic=self.pic)
        self._test_pic_cleared(user, user.profile.pic)

    def test_movie_pic_cleared(self):
        movie = Movie.objects.create(title='Movie', year=2015, slug='movie-2015', pic=self.pic)
        self._test_pic_cleared(movie, movie.pic)

    def test_director_pic_cleared(self):
        director = Director.objects.create(first='John', last='Doe', slug='john-doe', pic=self.pic)
        self._test_pic_cleared(director, director.pic)
