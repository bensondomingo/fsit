from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profiles.models import Profile
from profiles.api.serializers import ProfileSerializer


class ProfileAPIView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.profile.id)
