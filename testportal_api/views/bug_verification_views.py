from rest_framework import generics

from testportal.models import BugVerification

from testportal_api.serializers import BugVerificationSerializer


class BugVerificationList(generics.RetrieveUpdateDestroyAPIView):
    queryset = BugVerification.objects.all()
    serializer_class = BugVerificationSerializer


class BugVerificationDetail(generics.RetrieveDestroyAPIView):
   queryset = BugVerification.objects.all()
   serializer_class = BugVerificationSerializer
