from rest_framework import generics

from testportal.models import BugVerification

from testportal_api.serializers import BugVerificationSerializer


class BugVerificationList(generics.ListCreateAPIView):
    queryset = BugVerification.objects.all()
    serializer_class = BugVerificationSerializer


class BugVerificationDetail(generics.RetrieveUpdateDestroyAPIView):
   queryset = BugVerification.objects.all()
   serializer_class = BugVerificationSerializer
