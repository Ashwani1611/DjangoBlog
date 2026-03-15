from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"
        ordering            = ['name']


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('published', 'Published'),
    ]
    title      = models.CharField(max_length=200)
    content    = HTMLField()                          # ← TinyMCE rich text
    summary    = models.TextField(blank=True, null=True)
    tags       = models.CharField(max_length=300, blank=True, null=True)
    author     = models.ForeignKey(User, on_delete=models.CASCADE)
    category   = models.ForeignKey(
                    Category,
                    on_delete=models.SET_NULL,
                    null=True, blank=True
                 )
    image      = models.ImageField(
                    upload_to='post_images/',
                    blank=True, null=True
                 )
    image_url  = models.URLField(blank=True, null=True)   # ← image by URL
    video      = models.FileField(
                    upload_to='post_videos/',
                    blank=True, null=True
                 )
    video_url  = models.URLField(blank=True, null=True)   # ← video by URL
    status     = models.CharField(
                    max_length=10,
                    choices=STATUS_CHOICES,
                    default='draft'
                 )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_cover_image(self):
        # Returns uploaded image first, then URL image
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None

    def get_video(self):
        # Returns uploaded video first, then URL video
        if self.video:
            return self.video.url
        elif self.video_url:
            return self.video_url
        return None

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    post       = models.ForeignKey(
                    Post,
                    on_delete=models.CASCADE,
                    related_name='comments'
                 )
    author     = models.ForeignKey(User, on_delete=models.CASCADE)
    content    = models.TextField()
    sentiment  = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"