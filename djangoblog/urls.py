from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog import views as blog_views

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('api/',      include('blog.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('tinymce/',  include('tinymce.urls')),

    # Website pages
    path('',                         blog_views.home_view,            name='home'),
    path('post/<int:pk>/',           blog_views.post_detail_view,     name='post_detail'),
    path('post/create/',             blog_views.post_create_view,     name='post_create'),
    path('post/<int:pk>/edit/',      blog_views.post_edit_view,       name='post_edit'),
    path('post/<int:pk>/delete/',    blog_views.post_delete_view,     name='post_delete'),
    path('comment/<int:pk>/delete/', blog_views.comment_delete_view,  name='comment_delete'),
    path('category/create/',         blog_views.category_create_view, name='category_create'),  # ← THIS
    path('category/<slug:slug>/',    blog_views.category_posts_view,  name='category_posts'),
    path('search/',                  blog_views.search_view,           name='search'),
    path('register/',                blog_views.register_page_view,    name='register'),
    path('login/',                   blog_views.login_page_view,       name='login'),
    path('logout/',                  blog_views.logout_view_page,      name='logout'),
    path('upload-image/',            blog_views.upload_image,          name='upload_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)