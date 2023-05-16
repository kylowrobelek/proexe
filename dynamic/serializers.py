from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from dynamic.models import Column, DatabaseTable
from dynamic.utils import migrate_data


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

    def validate(self, attrs):
        # change from text to number can be not safe
        if (
            self.context.get("view")
            and (table_id := self.context["view"].kwargs.get("pk"))
            and (
                column := Column.objects.filter(
                    table_id=table_id, name=attrs["name"]
                ).first()
            )
        ):
            if column.type == "text" and attrs.get("type"):
                raise ValidationError("No backward compatibility")
        return super().validate(attrs)


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
            column["table_id"] = table.id
            Column.objects.create(**column)
        migrate_data(
            name=table.name,
            action="CREATE",
            fields=columns,
            app_label=__package__.rsplit(".", 1)[-1],
        )
        return table

    def update(self, instance, validated_data):
        columns = validated_data.pop("columns")
        serializer = ColumnSerializer(data=columns, many=True)
        serializer.is_valid(raise_exception=True)
        columns_to_alter = []
        columns_to_create = []
        for column in columns:
            query = Column.objects.filter(table_id=instance.id, name=column.get("name"))
            if query.exists():
                old_column = query.first()
                columns_to_alter.append(
                    {
                        "name": column.get("name"),
                        "type": column.get("type"),
                        "old_type": old_column.type,
                    }
                )
                query.update(type=column.get("type"))
            else:
                columns_to_create.append(column)
                column["table_id"] = instance.id
                Column.objects.create(**column)
        migrate_data(
            columns_to_alter + columns_to_create,
            instance.name,
            action="UPDATE",
            fields_to_create=columns_to_create,
            fields_to_update=columns_to_alter,
            app_label=__package__.rsplit(".", 1)[-1],
        )
        return instance


class DynamicSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model", None)
        self.Meta.model = model
        super(DynamicSerializer, self).__init__(*args, **kwargs)

    class Meta:
        fields = "__all__"
