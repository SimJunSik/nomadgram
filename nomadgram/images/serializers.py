from rest_framework import serializers
from . import models
from nomadgram.users import models as user_models
from taggit_serializer.serializers import (TagListSerializerField, TaggitSerializer)


class SmallImageSerializer(serializers.ModelSerializer) :

    class Meta :
        model = models.Image
        fields = (
            'file',
        )


class CountImageSerializer(serializers.ModelSerializer) :

    class Meta :
        model = models.Image
        fields = (
            'id',
            'file',
            'comment_count',
            'like_count',
        )

class FeedUserSerializers(serializers.ModelSerializer) :

    class Meta :
        model = user_models.User
        fields = (
            'username',
            'profile_image',
        )

class CommentSerializers(serializers.ModelSerializer) :

    creator = FeedUserSerializers(read_only=True)

    class Meta :
        model = models.Comment
        fields = (
            'id',
            'message',
            'creator'
        )


class LikeSerializers(serializers.ModelSerializer) :

    class Meta :
        model = models.Like
        fields = '__all__'


class ImageSerializers(TaggitSerializer, serializers.ModelSerializer) :

    comments = CommentSerializers(many=True)
    creator = FeedUserSerializers()
    tags = TagListSerializerField()

    class Meta :
        model = models.Image
        fields = (
            'id',
            'file',
            'location',
            'caption',
            'comments',
            'like_count',
            'creator',
            'tags',
            'created_at',
        )




class InputImageSerializer(serializers.ModelSerializer) :

    #file = serializers.FileField(required=False)

    class Meta :
        model = models.Image
        fields = (
            'file',
            'location',
            'caption',
        )