from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("settings", views.settings, name="settings"),
    path("follow/<str:username>", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("create_post", views.create_post, name="create_post"),
    path("post/<int:post_id>", views.post, name="post"),
    path("profile/<str:username>", views.profile, name="profile")
]
