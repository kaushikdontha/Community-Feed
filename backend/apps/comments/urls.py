from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('', views.CommentListCreateView.as_view(), name='comment-list'),
    path('<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('<int:pk>/vote/', views.vote_comment, name='vote-comment'),
    path('post/<int:post_id>/', views.PostCommentsView.as_view(), name='post-comments'),
]
