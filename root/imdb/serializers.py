from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):

    class UserProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = models.UserProfile
            fields = ('pic',)

    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = models.User
        fields = ('id', 'username', 'profile')


class MovieCommentSerializer(serializers.ModelSerializer):
    movie_id = serializers.PrimaryKeyRelatedField(read_only=True)
    user = UserSerializer(read_only=True)
    timestamp = serializers.DateTimeField(format='%m/%d/%Y %H:%M', read_only=True)

    class Meta:
        model = models.MovieComment
        fields = ('id', 'movie_id', 'user', 'timestamp', 'body')
