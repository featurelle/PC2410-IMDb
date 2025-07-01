from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

from . import models


class ProfileForm(forms.ModelForm):
    pic = forms.ImageField(label="Profile picture", required=False)

    class Meta:
        model = models.UserProfile
        fields = ['pic']


class UserAndProfileForm(UserChangeForm, ProfileForm):

    username = forms.CharField(label='Username', required=False)
    old_password = forms.CharField(label='Old password', required=False)
    new_password1 = forms.CharField(label='New password', required=False)
    new_password2 = forms.CharField(label='New password check', required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'pic']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            profile = self.instance.profile
        except models.UserProfile.DoesNotExist:
            profile = models.UserProfile.objects.create(user=self.instance)
        self.initial['pic'] = profile.pic

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if old_password and not self.instance.check_password(old_password):
            raise forms.ValidationError('Old password is incorrect.')
        return old_password

    def clean_new_password2(self):
        old_password = self.cleaned_data.get('old_password')
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')

        if not (old_password and new_password1 and new_password2):
            if new_password1 or new_password2 or old_password:
                raise forms.ValidationError('You must provide all three password inputs to set a new one.')
        else:
            if new_password1 != new_password2:
                raise forms.ValidationError('New passwords do not match.')
            elif new_password1 == old_password:
                raise forms.ValidationError('New password cannot be the same as old password.')
        return new_password2

    def clean(self):
        cleaned_data = super().clean()
        for field_name in self.fields.keys():
            if cleaned_data.get(field_name) == '':
                del cleaned_data[field_name]
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        profile = user.profile
        if username := self.cleaned_data.get('username'):
            user.username = username
        if email := self.cleaned_data.get('email'):
            user.email = email
        if self.cleaned_data.get('old_password') and (new_password := self.cleaned_data.get('new_password2')):
            user.set_password(new_password)
        if pic := self.cleaned_data.get('pic'):
            profile.pic = pic
        if commit:
            user.save()
            profile.save()
        return user
