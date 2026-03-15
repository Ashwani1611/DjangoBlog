from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('published', 'Published'),
    ]
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    summary    = models.TextField(blank=True, null=True)  # ← AI summary
    tags       = models.CharField(max_length=300, blank=True, null=True)  # ← AI tags
    author     = models.ForeignKey(User, on_delete=models.CASCADE)
    category   = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image      = models.ImageField(upload_to='post_images/', blank=True, null=True)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(User, on_delete=models.CASCADE)
    content    = models.TextField()
    sentiment  = models.CharField(max_length=20, blank=True, null=True)  # ← AI sentiment
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"