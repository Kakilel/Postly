from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.views.generic import *



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"] 

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    content = models.TextField()
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_posts", through="Like", blank=True)
    featured = models.BooleanField(default=False)
    published_date = models.DateTimeField(default=timezone.now)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_date", "-created_at"]

    def get_absolute_url(self):
        return reverse("App:post_detail", kwargs={"pk": self.pk})

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} likes {self.post}"

from django.db import models
from django.contrib.auth.models import User

class PostView(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='post_views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user', 'ip_address')