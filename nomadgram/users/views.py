from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models , serializers
from nomadgram.notifications import views as notification_views
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

class ExploreUsers(APIView) :

    def get(self, request, format=None) :
        
        last_five = models.User.objects.all().order_by('-date_joined')[:5]

        serializer = serializers.ListUserSerializer(last_five, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class FollowUser(APIView) :

    def post(self, request, user_id, format=None) :

        user = request.user

        try :
            user_to_follow = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)

        user.following.add(user_to_follow)
        user.save()

        notification_views.create_notification(user, user_to_follow, 'follow')

        return Response(status=status.HTTP_200_OK)


class UnFollowUser(APIView) :

    def post(self, request, user_id, format=None) :

        user = request.user

        try :
            user_to_follow = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)

        user.following.remove(user_to_follow)
        user.save()

        return Response(status=status.HTTP_200_OK)


class UserProfile(APIView) :

    def get_user(self, username) :

        try :
            found_user = models.User.objects.get(username=username)
            return found_user

        except models.User.DoesNotExist :
            return None

    def get(self, request, username, format=None) :

        found_user = self.get_user(username)

        if found_user is None :
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.UserProfileSerializer(found_user)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


    def put(self, request, username, format=None) :

        user = request.user

        found_user = self.get_user(username)

        if found_user is None :

            return Response(status=status.HTTP_404_NOT_FOUND)

        elif found_user.username != user.username :

            return Response(status=status.HTTP_401_UNAUTHORIZED)

        else :

            serializer = serializers.UserProfileSerializer(found_user, data=request.data, partial=True)

            if serializer.is_valid() :

                serializer.save()

                return Response(data=serializer.data, status=status.HTTP_200_OK)

            else :

                return Response(data=serializer.error, status=status.HTTP_400_BAD_REQUEST)

class UserFollwers(APIView) :

    def get(self, request, username, format=None) :

        try :
            found_user = models.User.objects.get(username=username)

        except models.User.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_followers = found_user.followers.all()

        serializer = serializers.ListUserSerializer(user_followers, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserFollwing(APIView) :

    def get(self, request, username, format=None) :

        try :
            found_user = models.User.objects.get(username=username)

        except models.User.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_following = found_user.following.all()

        serializer = serializers.ListUserSerializer(user_following, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


# function based view는 class based view에서 사용하는
# request.data 에 접근하지 못함
# function based view 에서는 
# request.POST.get('key') 어쩌구 저쩌구
# 이런식으로 접근해야 함
def UserFollowingFBV(request, username) :

    if request.method == 'GET' :

        try :
            found_user = models.User.objects.get(username=username)

        except models.User.DoesNotExist :
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_following = found_user.following.all()

        serializer = serializers.ListUserSerializer(user_following, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class Search(APIView) :

    def get(self, request, format=None) :

        username = request.query_params.get('username', None)

        if username is not None :
            
            users = models.User.objects.filter(username__istartswith=username)

            serializer = serializer.ListUserSerializer(users, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        else :

            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView) :

    def put(self, request, username,  format=None) :

        user = request.user

        if username == user.username :

            current_password = request.data.get('current_password', None)

            if current_password is not None :

                password_match = user.check_password(current_password)

                if password_match :

                    new_password = request.data.get('new_password', None)

                    if new_password is not None :

                        user.set_password(new_password)

                        user.save()

                        return Response(status=status.HTTP_200_OK)

                    else :

                        return Response(status=status.HTTP_400_BAD_REQUEST)

                else :

                    return Response(status=status.HTTP_400_BAD_REQUEST)

            else :

                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        else :

            return Response(status=status.HTTP_401_UNAUTHORIZED)

class FacebookLogin(SocialLoginView) :

    adapter_class = FacebookOAuth2Adapter





# from django.contrib.auth import get_user_model
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.urls import reverse
# from django.views.generic import DetailView, ListView, RedirectView, UpdateView

# User = get_user_model()


# class UserDetailView(LoginRequiredMixin, DetailView):

#     model = User
#     slug_field = "username"
#     slug_url_kwarg = "username"


# user_detail_view = UserDetailView.as_view()


# class UserListView(LoginRequiredMixin, ListView):

#     model = User
#     slug_field = "username"
#     slug_url_kwarg = "username"


# user_list_view = UserListView.as_view()


# class UserUpdateView(LoginRequiredMixin, UpdateView):

#     model = User
#     fields = ["name"]

#     def get_success_url(self):
#         return reverse("users:detail", kwargs={"username": self.request.user.username})

#     def get_object(self):
#         return User.objects.get(username=self.request.user.username)


# user_update_view = UserUpdateView.as_view()


# class UserRedirectView(LoginRequiredMixin, RedirectView):

#     permanent = False

#     def get_redirect_url(self):
#         return reverse("users:detail", kwargs={"username": self.request.user.username})


# user_redirect_view = UserRedirectView.as_view()
