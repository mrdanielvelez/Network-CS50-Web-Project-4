import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Default header pictures for new users
HEADER_PICS = [
    "https://images.unsplash.com/photo-1613967193490-1d17b930c1a1",
    "https://images.unsplash.com/photo-1614531341773-3bff8b7cb3fc",
    "https://images.unsplash.com/photo-1612059372972-a8284130ea68",
    "https://images.unsplash.com/photo-1442323794357-25b2ec110967",
    "https://images.unsplash.com/photo-1608665488977-b26949036f6e"
]

def random_header():
    return random.choice(HEADER_PICS)

class User(AbstractUser):
    name = models.CharField(max_length=25, blank=True)
    picture = models.URLField(default="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png")
    header = models.URLField(default=random_header)
    following = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="followers")

class Post(models.Model):
    content = models.CharField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Post by {self.author} | {self.date}"
