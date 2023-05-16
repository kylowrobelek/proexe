from django.apps import apps
from django.db import connection, models


def set_django_types(value):
    if value == "bool":
        return models.BooleanField(default=False)
    elif value == "text":
        return models.TextField(default="")
    elif value == "number":
        return models.IntegerField(default=0)


def create_model_schema(
    name,
    fields=None,
    app_label="",
    module="",
    options=None,
):
    if not module and app_label:
        module = app_label
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
        for field in fields:
            attrs.update({field["name"]: set_django_types(field["type"])})

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)
    apps.register_model("dynamic", model)
    return model


def migrate_data(
    fields,
    name,
    fields_to_update=None,
    fields_to_create=None,
    app_label="dynamic",
    action="",
):
    model = create_model_schema(name, fields, app_label=app_label)
    with connection.schema_editor() as schema_editor:
        if action == "CREATE":
            schema_editor.create_model(model)
        elif action == "UPDATE":
            for field_data in fields_to_update:
                old_field = set_django_types(field_data["old_type"])
                new_field = set_django_types(field_data["type"])
                old_field.name = (
                    old_field.column
                ) = new_field.name = new_field.column = field_data["name"]
                schema_editor.alter_field(model, old_field, new_field)
            for field_data in fields_to_create:
                field = set_django_types(field_data["type"])
                field.name = field.column = field_data["name"]
                schema_editor.add_field(model, field)
