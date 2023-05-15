from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from dynamic.models import DatabaseTable
from dynamic.serializers import TableSerializer


class DynamicTablesViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet):

    serializer_class = TableSerializer
    queryset = DatabaseTable.objects.all()
