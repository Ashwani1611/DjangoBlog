from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post, Category, Comment
from .serializers import PostSerializer, CategorySerializer, CommentSerializer
from .forms import PostForm, CommentForm, RegisterForm
from .ai_helper import (
    generate_summary,
    generate_tags,
    suggest_category,
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


# ─── AI API Endpoints ───────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def ai_summarize(request):
    content = request.data.get('content', '')
    if not content:
        return Response({'error': 'Content is required'}, status=400)
    summary = generate_summary(content)
    return Response({'summary': summary})


@api_view(['POST'])
@permission_classes([AllowAny])
def ai_generate_tags(request):
    title   = request.data.get('title', '')
    content = request.data.get('content', '')
    tags    = generate_tags(title, content)
    return Response({'tags': tags})


@api_view(['POST'])
@permission_classes([AllowAny])
def ai_suggest_category(request):
    title    = request.data.get('title', '')
    content  = request.data.get('content', '')
    category = suggest_category(title, content)
    return Response({'category': category})


@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat(request):
    question    = request.data.get('question', '')
    post_titles = list(Post.objects.filter(
                    status='published'
                  ).values_list('title', flat=True))
    answer = chat_with_blog(question, post_titles)
    return Response({'answer': answer})


# ─── Website Views ──────────────────────────────────────────

def home_view(request):
    posts = Post.objects.filter(status='published')
    return render(request, 'blog/home.html', {'posts': posts})


def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment           = form.save(commit=False)
            comment.post      = post
            comment.author    = request.user
            # AI sentiment check
            comment.sentiment = check_sentiment(comment.content)
            comment.save()
            return redirect('post_detail', pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post, 'form': form})


@login_required
def post_create_view(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post        = form.save(commit=False)
            post.author = request.user
            # AI features auto-applied on save
            post.summary = generate_summary(post.content)
            post.tags    = generate_tags(post.title, post.content)
            post.save()
            return redirect('home')
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create Post'})


def search_view(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query),
        status='published'
    )
    return render(request, 'blog/search.html', {'posts': posts, 'query': query})


def register_page_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
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