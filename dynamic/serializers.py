from django.db import transaction
from rest_framework import serializers

from dynamic.models import DatabaseTable, Column


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
        for column in columns:
            column['table_id'] = table.id
            serializer = ColumnSerializer(data=column)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return table

