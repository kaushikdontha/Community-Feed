from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostListCreateView.as_view(), name='post-list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/vote/', views.vote_post, name='vote-post'),
    path('user/<str:username>/', views.UserPostsView.as_view(), name='user-posts'),
]
