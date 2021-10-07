from django.urls import path
from .views import (
    PostListView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    PostDetailView,
)
from . import views

app_name = 'blog'


urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('search/', views.search, name='search-results'),
    path('user/<int:pk>/', views.user_posts_view, name='user-posts'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    # path('post/<slug:slug>/', views.post_detail_view, name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),

    path('like/post/', views.like_post, name='like-post'),
    path('dislike/post/', views.dislike_post, name='dislike-post'),
]
