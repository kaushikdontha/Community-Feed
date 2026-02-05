from django.urls import path
from . import views

app_name = 'communities'

urlpatterns = [
    path('', views.CommunityListCreateView.as_view(), name='community-list'),
    path('<slug:slug>/', views.CommunityDetailView.as_view(), name='community-detail'),
    path('<slug:slug>/join/', views.join_community, name='join-community'),
    path('<slug:slug>/leave/', views.leave_community, name='leave-community'),
]
