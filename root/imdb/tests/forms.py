from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from ..models import UserProfile
from ..forms import UserAndProfileForm


class UserAndProfileFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = UserProfile.objects.create(user=self.user)

    def tearDown(self):
        self.user.delete()

    def test_empty_form(self):
        data = {
            'username': '',
            'email': '',
            'old_password': '',
            'new_password1': '',
            'new_password2': ''
        }
        form = UserAndProfileForm(data, {'pic': None}, instance=self.user)

        self.assertTrue(form.is_valid(), msg=form.errors.as_data())
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, '')
        self.assertTrue(user.check_password('testpass'))
        self.assertEqual(user.profile.pic, None)

    def test_full_valid_form(self):
        # Create a valid form with new password and profile pic
        data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'old_password': 'testpass',
            'new_password1': 'testpass1',
            'new_password2': 'testpass1'
        }
        file = SimpleUploadedFile(
            "test.jpg",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04"
            b"\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/jpeg"
        )
        form = UserAndProfileForm(data, {'pic': file}, instance=self.user)

        self.assertTrue(form.is_valid(), msg=form.errors.as_data())
        user = form.save()
        self.assertEqual(user.username, 'newusername')
        self.assertEqual(user.email, 'newemail@example.com')
        self.assertTrue(user.check_password('testpass1'))
        self.assertEqual(user.profile.pic.name, 'imdb/users/test.jpg')

    def test_only_valid_userdata(self):
        # Create a valid form with new password and profile pic
        data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
        }
        file = SimpleUploadedFile(
            "test.jpg",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04"
            b"\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/jpeg"
        )
        form = UserAndProfileForm(data, {'pic': file}, instance=self.user)

        self.assertTrue(form.is_valid(), msg=form.errors.as_data())
        user = form.save()
        self.assertEqual(user.username, 'newusername')
        self.assertEqual(user.email, 'newemail@example.com')
        self.assertEqual(user.profile.pic.name, 'imdb/users/test.jpg')

    def test_only_incomplete_password_set(self):
        # Test clean_old_password only
        data_sets = [
            {'old_password': 'testpass'},
            {'new_password1': 'testpass'},
            {'new_password2': 'testpass'}
        ]
        form = UserAndProfileForm(data_sets[0], instance=self.user)
        self.assertFalse(form.is_valid())
        form = UserAndProfileForm(data_sets[1], instance=self.user)
        self.assertFalse(form.is_valid())
        form = UserAndProfileForm(data_sets[2], instance=self.user)
        self.assertFalse(form.is_valid())
        form = UserAndProfileForm(data_sets[0] | data_sets[1], instance=self.user)
        self.assertFalse(form.is_valid())
        form = UserAndProfileForm(data_sets[1] | data_sets[2], instance=self.user)
        self.assertFalse(form.is_valid())
        form = UserAndProfileForm(data_sets[0] | data_sets[2], instance=self.user)
        self.assertFalse(form.is_valid())

    def test_only_complete_password_set(self):
        # Test clean_old_password method with incorrect password
        data = {'old_password': 'wrongpass', 'new_password1': 'testpass1', 'new_password2': 'testpass1'}
        form = UserAndProfileForm(data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('Old password is incorrect.', form.errors['old_password'])

        # Test clean_new_password2 method with matching passwords
        data = {'old_password': 'testpass', 'new_password1': 'newtestpass', 'new_password2': 'newtestpass'}
        form = UserAndProfileForm(data, instance=self.user)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['old_password'], 'testpass')
        self.assertEqual(form.cleaned_data['new_password2'], 'newtestpass')

        # Test clean_new_password2 method with non-matching passwords
        data = {'old_password': 'testpass', 'new_password1': 'newtestpass1', 'new_password2': 'newtestpass2'}
        form = UserAndProfileForm(data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('New passwords do not match.', form.errors['new_password2'])

        # Test clean_new_password2 method with same old and new passwords
        data = {'old_password': 'testpass', 'new_password1': 'testpass', 'new_password2': 'testpass'}
        form = UserAndProfileForm(data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('New password cannot be the same as old password.', form.errors['new_password2'])
