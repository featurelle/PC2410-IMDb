from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase

from ..models import User, UserProfile, Movie
from ..serializers import UserSerializer, MovieCommentSerializer


class UserSerializerTestCase(TestCase):
    def setUp(self):
        profile_pic = SimpleUploadedFile(
            "profile_pic.jpg",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04"
            b"\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/jpeg"
        )
        self.user = User.objects.create(username='testuser')
        self.user_profile = UserProfile.objects.create(user=self.user, pic=profile_pic)

    def tearDown(self):
        self.user.delete()

    def test_serializer(self):
        serializer = UserSerializer(instance=self.user)
        expected_data = {
            'id': self.user.id,
            'username': 'testuser',
            'profile': {
                'pic': '/media/imdb/users/profile_pic.jpg'
            }
        }
        self.assertEqual(serializer.data, expected_data)


class MovieCommentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.movie = Movie.objects.create(title='Test Movie', year='2015', slug='test-movie-2015')
        self.comment_data = {
            'body': 'Test comment'
        }

    def test_serializer_with_valid_data(self):
        serializer = MovieCommentSerializer(data=self.comment_data)
        self.assertTrue(serializer.is_valid())
        comment = serializer.save(user=self.user, movie_id=self.movie.id)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.movie, self.movie)
        self.assertEqual(comment.body, self.comment_data['body'])

    def test_serializer_with_missing_user(self):
        serializer = MovieCommentSerializer(data=self.comment_data)
        serializer.is_valid()
        with self.assertRaises(IntegrityError):
            serializer.save(movie_id=self.movie.id)

    def test_serializer_with_missing_movie(self):
        serializer = MovieCommentSerializer(data=self.comment_data)
        serializer.is_valid()
        with self.assertRaises(IntegrityError):
            serializer.save(user=self.user)

    def test_serializer_with_missing_body(self):
        self.comment_data.pop('body')
        serializer = MovieCommentSerializer(data=self.comment_data)
        self.assertFalse(serializer.is_valid())
