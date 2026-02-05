from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes as perms
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileUpdateSerializer,
    LeaderboardSerializer,
)
from .models import KarmaTransaction

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """Handle user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveAPIView):
    """Get any user's public profile by username."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [permissions.AllowAny]


class CurrentUserView(APIView):
    """Get the current authenticated user's data."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@api_view(['GET'])
@perms([permissions.AllowAny])
def leaderboard_24h(request):
    """
    Get the 24-hour karma leaderboard.
    
    CONSTRAINT: Daily karma is NOT stored as a simple integer field.
    It is calculated DYNAMICALLY from KarmaTransaction history.
    
    This approach:
    - Accurately reflects karma earned in exactly the last 24 hours
    - Prevents gaming by storing immutable transaction history
    - Handles timezone correctly
    """
    yesterday = timezone.now() - timedelta(hours=24)
    limit = int(request.query_params.get('limit', 10))
    limit = min(limit, 100)  # Cap at 100
    
    # Aggregate karma from transactions in the last 24 hours
    # Uses a single efficient query with GROUP BY
    leaderboard = KarmaTransaction.objects.filter(
        created_at__gte=yesterday
    ).values(
        'user__id',
        'user__username',
        'user__avatar',
    ).annotate(
        karma_24h=Sum('delta')
    ).order_by('-karma_24h')[:limit]
    
    # Format response
    result = []
    for rank, entry in enumerate(leaderboard, 1):
        result.append({
            'rank': rank,
            'user_id': entry['user__id'],
            'username': entry['user__username'],
            'avatar': entry['user__avatar'],
            'karma_24h': entry['karma_24h'] or 0,
        })
    
    return Response({
        'period': '24h',
        'generated_at': timezone.now().isoformat(),
        'leaderboard': result,
    })


@api_view(['GET'])
@perms([permissions.AllowAny])
def leaderboard_all_time(request):
    """Get the all-time karma leaderboard (uses cached karma field for efficiency)."""
    limit = int(request.query_params.get('limit', 10))
    limit = min(limit, 100)
    
    users = User.objects.order_by('-karma')[:limit]
    
    result = []
    for rank, user in enumerate(users, 1):
        result.append({
            'rank': rank,
            'user_id': user.id,
            'username': user.username,
            'avatar': user.avatar.url if user.avatar else None,
            'karma': user.karma,
        })
    
    return Response({
        'period': 'all_time',
        'generated_at': timezone.now().isoformat(),
        'leaderboard': result,
    })
