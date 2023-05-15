from django.apps import apps
from django.conf import settings
from django.db import connection, models
from importlib import reload, import_module

from dynamic.models import DatabaseTable, Column

def set_django_types(value):
    if value == "bool":
        return models.BooleanField(default=False)
    elif value == "text":
        return models.TextField(default="")
    elif value == "number":
        return models.IntegerField(default=0)


def dynamic_modeling(table_name, columns, action="CREATE"):
    django_fields = {}
    for column in columns:
        django_fields[column["name"]] = set_django_types(column["type"])
    return create_model_schema(
        table_name, action=action, fields=django_fields, app_label="dynamic", module="dynamic")


def create_model_schema(
        name,
        fields=None,
        app_label="",
        module="",
        options=None,
        migrations=True,
        action=""
):
    """
    Create specified model
    """

    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, "app_label", app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {"__module__": module, "Meta": Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)
    apps.register_model("dynamic", model)
    if migrations:
        migrate_data(
            fields=fields,
            name=name,
            app_label=app_label,
            options=options,
            module=module,
            action=action
        )
    print(f"a tu? {model.objects.count()}")
    return model


def migrate_data(fields, name, app_label, options, module, action=""):

    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, "app_label", app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {"__module__": module, "Meta": Meta}

    if fields:
        attrs.update(fields)

    model = type(name, (models.Model,), attrs)

    with connection.schema_editor() as schema_editor:
        if action == "CREATE":
            schema_editor.create_model(model)
            # for name, field in fields.items():
            #     field.name = field.column = name
            #     schema_editor.add_field(model, field)
        apps.register_model("dynamic", model)
        print(f"w srodku {model.objects.count()}")
        reload(import_module(settings.ROOT_URLCONF))
        # elif action == "UPDATE":
        #     field_tuple = list(column_fields.items())[0]
        #     column_db = Column.objects.get(table__name=name, name=field_tuple[0])
        #     old_column_field = set_django_types(fields["old_type"])
        #     old_column_field.name = column_db.name
        #     old_column_field.column = column_db.name
        #     field = field_tuple[1]
        #     field.name = field.column = field_tuple[0]
        #     schema_editor.alter_field(model, old_column_field, field)
        #     column_db.save()

