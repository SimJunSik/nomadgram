from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models , serializers
from nomadgram.notifications import views as notification_views
from nomadgram.users import models as user_models
from nomadgram.users import serializers as user_serializers


class Images(APIView) :

    def get(self, request, format=None) :

        user = request.user
        
        following_users = user.following.all()

        #print(following_users)

        image_list = []

        for following_user in following_users :

            #print(following_user.images.all()[:2])

            user_images = following_user.images.all()[:2]

            for image in user_images :

                image_list.append(image)

        my_images = user.images.all()[:2]

        for image in my_images :

            image_list.append(image)

        #print(image_list)

        #sorted_list = sorted(image_list, key=get_key, reverse=True)
        sorted_list = sorted(image_list, key=lambda image : image.created_at, reverse=True)

        #print(sorted_list)

        serializer = serializers.ImageSerializers(sorted_list, many=True)

        return Response(data = serializer.data)

    def post(self, request, format=None) :
        
        user = request.user

        serializer = serializers.InputImageSerializer(data=request.data)

        if serializer.is_valid() :

            serializer.save(creator=user)

            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        else :

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_key(image) :
    return image.created_at


class LikeImage(APIView) :

    def get(self, request, image_id, format=None) :

        likes = models.Like.objects.filter(image__id=image_id)

        like_creators_ids = likes.values('creator_id')

        users = user_models.User.objects.filter(id__in=like_creators_ids)

        serializer = user_serializers.ListUserSerializer(users, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, image_id, format=None) :

        user = request.user

        try :
            found_image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist :
            return Response(status=404)

        try :
            preexisting_like = models.Like.objects.get(
                creator = user,
                image = found_image,
            )

            return Response(status=status.HTTP_304_NOT_MODIFIED)

        except models.Like.DoesNotExist :
            new_like = models.Like.objects.create(
                creator = user,
                image = found_image,
            )
            new_like.save()

            notification_views.create_notification(user, found_image.creator, 'like', found_image)

            return Response(status=status.HTTP_201_CREATED)


class UnLikeImage(APIView) :

    def delete(self, request, image_id, format=None) :

        user = request.user

        try :
            found_image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist :
            return Response(status=404)


        try :
            preexisting_like = models.Like.objects.get(
                creator = user,
                image = found_image,
            )
            preexisting_like.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except models.Like.DoesNotExist :

            return Response(status=status.HTTP_304_NOT_MODIFIED)


class CommentOnImage(APIView) :

    def post(self, request, image_id, format=None) :

        user = request.user

        #print(user)

        try :
            found_image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)


        serializer = serializers.CommentSerializers(data=request.data)

        if serializer.is_valid() :

            serializer.save(creator=user, image=found_image)

            notification_views.create_notification(user, found_image.creator, 'comment', found_image, serializer.data['message'])

            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        else :

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Comment(APIView) :

    def delete(self, request, comment_id, format=None) :

        user = request.user

        try :
            comment = models.Comment.objects.get(id=comment_id, creator=user)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.Comment.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)


class Search(APIView) :

    def get(self, request, format=None) :

        hashtags = request.query_params.get('hashtags', None)

        if hashtags is not None :

            hashtags = hashtags.split(',')

            # hashtags 안에 있는 hashtag들을 or로 검색
            images = models.Image.objects.filter(tags__name__in=hashtags).distinct()

            serializer = serializers.CountImageSerializer(images, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)
            """
            another ex>
            title: 'hello',
            location : 'bogota',
            creator: {
                id: 1 ,
                username : 'nomadmin'
            }

            models.Image.objects.filter(creator__username__icontains='Noma')
            > deep relationship
            > icontains는 대소문자 구분 X
            > iexact는 대소문자 구분 안하면서 정확히 일치하게
            """

        else :

            return Response(status=status.HTTP_400_BAD_REQUEST)


class ModerateComment(APIView) :

    def delete(self, request, image_id, comment_id, format=None) :

        user = request.user

        try :
            comment_to_delete = models.Comment.objects.get(id=comment_id, image__id=image_id, image__creator=user)
            comment_to_delete.delete()
        except models.Comment.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageDetail(APIView) :

    def find_on_image(self, image_id, user) :

        try :
            image = models.Image.objects.get(id=image_id, creator=user)
            return image
        except models.Image.DoesNotExist :
            return None


    def get(self, request, image_id, format=None) :

        user = request.user

        try :
            image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.ImageSerializers(image)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    
    def put(self, request, image_id, format=None) :

        user = request.user

        image = self.find_on_image(image_id, user)

        if image is None :

            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.InputImageSerializer(image, data=request.data, partial=True)

        if serializer.is_valid() :

            serializer.save(creator=user)

            return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)

        else :

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, image_id, format=None) :

        user = request.user

        image = self.find_on_image(image_id, user)

        if image is None :

            return Response(status=status.HTTP_401_UNAUTHORIZED)

        image.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

        
# class ListAllImages(APIView) :

#     def get(self, request, format=None) :

#         all_images = models.Image.objects.all()

#         serializer = serializers.ImageSerializers(all_images, many=True)

#         return Response(data=serializer.data)


# class ListAllComments(APIView) :

#     def get(self, request, format=None) :

#         user_id = request.user.id

#         all_comments = models.Comment.objects.filter(creator = user_id)

#         serializer = serializers.CommentSerializers(all_comments, many=True)

#         return Response(data=serializer.data)


# class ListAllLikes(APIView) :

#     def get(self, request, format=None) :

#         all_likes = models.Like.objects.all()

#         serializer = serializers.LikeSerializers(all_likes, many=True)

#         return Response(data=serializer.data)