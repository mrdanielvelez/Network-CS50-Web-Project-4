import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, resolve_url
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import *

MAX_POST_LENGTH = 280

def index(request):
    posts = Post.objects.all().order_by("-date")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj": page_obj
    })

def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile).order_by("-date")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "profile": profile,
        "page_obj": page_obj
    })

@login_required
def following(request):
    followed_users = request.user.following.all()
    posts = list(Post.objects.filter(author__in=followed_users).order_by("-date"))
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })

@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        length = len(content)
        if length < 0:
            messages.add_message(request, messages.ERROR, "Post cannot be empty.")
            return HttpResponseRedirect(reverse("index"))
        elif length > MAX_POST_LENGTH:
            messages.add_message(request, messages.ERROR, "Maximum post length: 280 characters")
            return HttpResponseRedirect(reverse("index"))
        else:
            post = Post(content=content, author=request.user)
            post.save()
            return HttpResponseRedirect(reverse("index"))

@login_required
def follow(request, username):
    profile = get_object_or_404(User, username=username)
    if request.method == "POST" and request.user != profile:
        if profile not in request.user.following.all():
            request.user.following.add(profile)
        else:
            request.user.following.remove(profile)
        return HttpResponseRedirect(resolve_url("profile", username=username))

@login_required
@csrf_exempt
def post(request, post_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    data = json.loads(request.body)

    if "toggle_like" in data:
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

    if "content" in data:
        if not 0 < len(data["content"]) <= MAX_POST_LENGTH:
            return JsonResponse({"error": "Invalid post length."}, status=400)
        elif request.user != post.author:
            return JsonResponse({"error": "Unauthorized edit."}, status=401)
        else:
            post.content = data["content"]

    post.save()
    return JsonResponse({"num_likes": post.likes.count()}, status=201)


@login_required
def settings(request):
    if request.method == "POST":
        display_name = request.POST["display_name"]
        if not 0 < len(display_name) <= 25:
            return render(request, "network/settings.html", {
                "message": "Invalid display name. Max length: 25 characters"
            }) 
        profile_pic = request.POST["profile_pic"]
        header_pic = request.POST["header_pic"]
        request.user.name = display_name
        request.user.picture = profile_pic
        request.user.header = header_pic
        request.user.save()
        return HttpResponseRedirect(resolve_url("profile", username=request.user.username))

    return render(request, "network/settings.html")

def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Ensure name field is valid
        if not 0 < len(name) <= 25:
            return render(request, "network/register.html", {
                "message": "Invalid display name."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, email=email, password=password, name=name)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

