from rest_framework import generics

from testportal.models import Tag

from testportal_api.serializers import TagSerializer


class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagDetail(generics.RetrieveDestroyAPIView):
   queryset = Tag.objects.all()
   serializer_class = TagSerializer
