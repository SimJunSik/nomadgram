from django.urls import path
from . import views

# from nomadgram.users.views import (
#     user_list_view,
#     user_redirect_view,
#     user_update_view,
#     user_detail_view,
# )

app_name = "users"
urlpatterns = [
    path("explore/", view=views.ExploreUsers.as_view(), name="explore_users"),
    path('<int:user_id>/follow/', view=views.FollowUser.as_view(),name='follow_user'),
    path('<int:user_id>/unfollow/', view=views.UnFollowUser.as_view(),name='unfollow_user'),
    path('search/', view=views.Search.as_view(), name='search'),
    path('<str:username>/',view=views.UserProfile.as_view(), name='user_profile'),
    path('<str:username>/password/',view=views.ChangePassword.as_view(), name='change'),
    path('<str:username>/followers/', view=views.UserFollwers.as_view(), name='user_followers'),
    path('<str:username>/following/', view=views.UserFollwing.as_view(), name='user_following'),
    path('login/facebook/', view=views.FacebookLogin.as_view(), name='fb_login'),
    # path("~redirect/", view=user_redirect_view, name="redirect"),
    # path("~update/", view=user_update_view, name="update"),
    # path("<str:username>/", view=user_detail_view, name="detail"),
]