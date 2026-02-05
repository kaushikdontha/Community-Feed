from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Leaderboards - 24h karma calculated dynamically from KarmaTransaction
    path('leaderboard/24h/', views.leaderboard_24h, name='leaderboard-24h'),
    path('leaderboard/', views.leaderboard_all_time, name='leaderboard-all'),
    
    path('<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
]
