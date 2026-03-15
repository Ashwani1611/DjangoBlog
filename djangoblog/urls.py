"""
URL configuration for djangoblog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog import views as blog_views

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('api/',      include('blog.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # Website pages
    path('',               blog_views.home_view,          name='home'),
    path('post/<int:pk>/', blog_views.post_detail_view,   name='post_detail'),
    path('post/create/',   blog_views.post_create_view,   name='post_create'),
    path('search/',        blog_views.search_view,         name='search'),
    path('register/',      blog_views.register_page_view,  name='register'),
    path('login/',         blog_views.login_page_view,     name='login'),
    path('logout/',        blog_views.logout_view_page,    name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)