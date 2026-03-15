from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from .models import Post, Category, Comment
from .serializers import PostSerializer, CategorySerializer, CommentSerializer
from .forms import PostForm, CommentForm, RegisterForm, CategoryForm
from .ai_helper import (
    generate_summary,
    generate_tags,
    check_sentiment,
    chat_with_blog
)


# ─── API Views ──────────────────────────────────────────────

class PostViewSet(viewsets.ModelViewSet):
    queryset           = Post.objects.filter(status='published')
    serializer_class   = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['title', 'content']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    queryset           = Comment.objects.all()
    serializer_class   = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ─── Image Upload for TinyMCE ───────────────────────────────

@csrf_exempt
@login_required(login_url='/login/')
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload   = request.FILES['file']
        ext      = os.path.splitext(upload.name)[1].lower()
        allowed  = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if ext not in allowed:
            return JsonResponse({'error': 'File type not allowed'}, status=400)
        # Save to media folder
        from django.core.files.storage import default_storage
        path = default_storage.save(f'tinymce/{upload.name}', upload)
        url  = f'/media/{path}'
        return JsonResponse({'location': url})
    return JsonResponse({'error': 'No file uploaded'}, status=400)


# ─── AI API Endpoints ───────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def ai_summarize(request):
    content = request.data.get('content', '')
    if not content:
        return Response({'error': 'Content required'}, status=400)
    return Response({'summary': generate_summary(content)})


@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat(request):
    question = request.data.get('question', '')
    post_id  = request.data.get('post_id', None)
    if post_id:
        try:
            post      = Post.objects.get(pk=post_id)
            post_data = [{'title': post.title, 'content': post.content}]
        except Post.DoesNotExist:
            post_data = []
    else:
        post_data = list(Post.objects.filter(
            status='published'
        ).values('title', 'content'))
    answer = chat_with_blog(question, post_data)
    return Response({'answer': answer})


# ─── Website Views ──────────────────────────────────────────

def home_view(request):
    posts      = Post.objects.filter(status='published')
    categories = Category.objects.all()
    return render(request, 'blog/home.html', {
        'posts':      posts,
        'categories': categories
    })


def category_posts_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts    = Post.objects.filter(
                 status='published',
                 category=category
               )
    return render(request, 'blog/category_posts.html', {
        'category': category,
        'posts':    posts
    })


def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to comment.')
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment           = form.save(commit=False)
            comment.post      = post
            comment.author    = request.user
            comment.sentiment = check_sentiment(comment.content)
            comment.save()
            return redirect('post_detail', pk=pk)
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'form': form
    })


@login_required(login_url='/login/')
def post_create_view(request):
    cat_form = CategoryForm()
    form     = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post         = form.save(commit=False)
            post.author  = request.user
            post.summary = generate_summary(post.content)
            post.tags    = generate_tags(post.title, post.content)
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', pk=post.pk)
    return render(request, 'blog/post_form.html', {
        'form':     form,
        'cat_form': cat_form,
        'title':    'Create Post'
    })


@login_required(login_url='/login/')
def category_create_view(request):
    if request.method == 'POST':
        import json
        try:
            # Read JSON data from request
            data        = json.loads(request.body)
            name        = data.get('name', '').strip()
            description = data.get('description', '').strip()

            if not name:
                return JsonResponse({'error': 'Name is required'}, status=400)

            # Check if category already exists
            if Category.objects.filter(name__iexact=name).exists():
                return JsonResponse({'error': 'Category already exists'}, status=400)

            # Create category
            from django.utils.text import slugify
            category = Category.objects.create(
                name        = name,
                slug        = slugify(name),
                description = description
            )
            return JsonResponse({
                'id':   category.id,
                'name': category.name,
                'slug': category.slug
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required(login_url='/login/')
def post_edit_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You are not allowed to edit this post.')
        return redirect('post_detail', pk=pk)
    form = PostForm(instance=post)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=pk)
    return render(request, 'blog/post_form.html', {
        'form':  form,
        'title': 'Edit Post'
    })


@login_required(login_url='/login/')
def post_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You are not allowed to delete this post.')
        return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required(login_url='/login/')
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if (comment.author    != request.user and
        comment.post.author != request.user and
        not request.user.is_staff):
        messages.error(request, 'You are not allowed to delete this comment.')
        return redirect('post_detail', pk=post_pk)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted!')
    return redirect('post_detail', pk=post_pk)


def search_view(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query),
        status='published'
    )
    return render(request, 'blog/search.html', {
        'posts': posts,
        'query': query
    })


def register_page_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'blog/register.html', {'form': form})


def login_page_view(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        error = 'Invalid username or password'
    return render(request, 'blog/login.html', {'error': error})


def logout_view_page(request):
    logout(request)
    return redirect('home')