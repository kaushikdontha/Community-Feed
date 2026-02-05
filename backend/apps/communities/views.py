from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Community, CommunityMembership
from .serializers import (
    CommunitySerializer,
    CommunityCreateSerializer,
    CommunityListSerializer,
)


class CommunityListCreateView(generics.ListCreateAPIView):
    """List all communities or create a new one."""
    
    queryset = Community.objects.filter(is_private=False)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommunityCreateSerializer
        return CommunityListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class CommunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a community."""
    
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_update(self, serializer):
        # Only moderators can update
        if self.request.user not in serializer.instance.moderators.all():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only moderators can edit this community.")
        serializer.save()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_community(request, slug):
    """Join a community."""
    try:
        community = Community.objects.get(slug=slug)
    except Community.DoesNotExist:
        return Response(
            {'error': 'Community not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if community.members.filter(id=request.user.id).exists():
        return Response(
            {'error': 'Already a member'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    CommunityMembership.objects.create(user=request.user, community=community)
    return Response({'message': f'Joined c/{community.name}'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_community(request, slug):
    """Leave a community."""
    try:
        community = Community.objects.get(slug=slug)
    except Community.DoesNotExist:
        return Response(
            {'error': 'Community not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    membership = CommunityMembership.objects.filter(
        user=request.user,
        community=community
    ).first()
    
    if not membership:
        return Response(
            {'error': 'Not a member'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    membership.delete()
    return Response({'message': f'Left c/{community.name}'})
