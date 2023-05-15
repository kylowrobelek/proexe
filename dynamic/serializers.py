from django.db import transaction
from rest_framework import serializers

from dynamic.models import Column, DatabaseTable
from dynamic.utils import dynamic_modeling


def set_django_serializer_types(value):
    if value == "bool":
        return serializers.BooleanField()
    elif value == "text":
        return serializers.CharField()
    elif value == "number":
        return serializers.IntegerField()


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = "__all__"


class TableSerializer(serializers.ModelSerializer):
    columns = ColumnSerializer(many=True)

    class Meta:
        model = DatabaseTable
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        columns = validated_data.pop("columns")
        table = super().create(validated_data)
        serializer = ColumnSerializer(data=columns, many=True)
        serializer.is_valid(raise_exception=True)
        for column in columns:
            column['table_id'] = table.id
            Column.objects.create(**column)
        dynamic_modeling(table.name, columns)
        return table


class DynamicSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model', None)
        self.Meta.model = model
        super(DynamicSerializer, self).__init__(*args, **kwargs)

    class Meta:
        fields = "__all__"
