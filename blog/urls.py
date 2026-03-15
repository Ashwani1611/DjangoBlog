from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views
from . import jwt_views

router = DefaultRouter()
router.register(r'posts',      views.PostViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'comments',   views.CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Token auth
    path('auth/register/', auth_views.register_view),
    path('auth/login/',    auth_views.login_view),
    path('auth/logout/',   auth_views.logout_view),
    path('auth/profile/',  auth_views.profile_view),

    # JWT auth
    path('jwt/register/', jwt_views.jwt_register_view),
    path('jwt/login/',    jwt_views.jwt_login_view),
    path('jwt/logout/',   jwt_views.jwt_logout_view),
    path('jwt/refresh/',  jwt_views.jwt_refresh_view),
    path('jwt/profile/',  jwt_views.jwt_profile_view),

    # AI endpoints
    path('ai/summarize/',        views.ai_summarize),
    path('ai/tags/',             views.ai_generate_tags),
    path('ai/suggest-category/', views.ai_suggest_category),
    path('ai/chat/',             views.ai_chat),
]