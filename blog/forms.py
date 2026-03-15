from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from tinymce.widgets import TinyMCE
from .models import Post, Comment, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model  = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'e.g. Technology'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows':  2
            }),
        }


class PostForm(forms.ModelForm):
    # Image options
    image_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class':       'form-control',
            'placeholder': 'https://example.com/image.jpg'
        }),
        label='Cover image URL'
    )

    # Video options
    video_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class':       'form-control',
            'placeholder': 'https://youtube.com/watch?v=... or video link'
        }),
        label='Video URL (YouTube or direct link)'
    )

    class Meta:
        model  = Post
        fields = [
            'title', 'content', 'category',
            'image', 'image_url',
            'video', 'video_url',
            'status'
        ]
        widgets = {
            'title':   forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'Enter post title...'
            }),
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'category':forms.Select(attrs={'class': 'form-select'}),
            'image':   forms.FileInput(attrs={'class': 'form-control'}),
            'video':   forms.FileInput(attrs={'class': 'form-control'}),
            'status':  forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required    = False
        self.fields['video'].required    = False
        self.fields['category'].empty_label = '--- Select category ---'
        # Show only existing categories
        self.fields['category'].queryset = Category.objects.all().order_by('name')


class CommentForm(forms.ModelForm):
    class Meta:
        model  = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class':       'form-control',
                'rows':        3,
                'placeholder': 'Write a comment...'
            })
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'