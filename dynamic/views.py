from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from dynamic.models import DatabaseTable, Column
from dynamic.serializers import (
    DynamicSerializer,
    TableSerializer,
    set_django_serializer_types,
)
from dynamic.utils import create_model_schema, set_django_types


class DynamicTablesViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    serializer_class = TableSerializer
    queryset = DatabaseTable.objects.all()

    def get_django_columns(self, table_id):
        columns = Column.objects.filter(table_id=table_id).values_list("name", "type")
        fields = {}
        for data in columns:
            fields[data[0]] = set_django_serializer_types(data[1])
        return fields

    def get_django_model(self, pk):
        table_name = self.get_object().name
        columns = list(Column.objects.filter(table_id=pk).values("name", "type"))
        return create_model_schema(
            table_name, fields=columns, app_label=__package__.rsplit(".", 1)[-1]
        )

    @action(detail=True, methods=("post",))
    def row(self, request, pk):
        model = self.get_django_model(pk)
        serializer = DynamicSerializer(data=request.data, model=model)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=("get",))
    def rows(self, request, pk):
        model = self.get_django_model(pk)
        serializer = DynamicSerializer(model.objects.all(), many=True, model=model)
        return Response(serializer.data)
