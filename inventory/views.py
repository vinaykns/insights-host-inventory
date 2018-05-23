from django.shortcuts import render

from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Entity, Tag
from .serializers import EntitySerializer, TagSerializer


class EntityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows entities to be viewed or edited.
    """
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

    _valid_fields = [f.name for f in Entity._meta.get_fields()]

    def get_queryset(self):

        qs = self.queryset

        for k, vs in self.request.GET.lists():
            if any(k.startswith(n) for n in self._valid_fields):
                for v in vs:
                    if k.endswith("__in"):
                        v = v.split("|")
                    qs = qs.filter(**{k: v})

        return qs


    def create(self, request):

        def _get_or_create_tag(obj):
            if isinstance(obj, dict):
                ser = TagSerializer(data=obj)
                ser.is_valid(raise_exception=True)
                tag, created = Tag.objects.get_or_create(**obj)
                return TagSerializer(tag, context={"request": request})["url"].value
            else:
                return obj

        request.data["tags"] = [_get_or_create_tag(t) for t in request.data.get("tags", [])]
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
