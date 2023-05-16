from django.test import TestCase
from rest_framework.test import APIClient

from dynamic.models import Column, DatabaseTable
from dynamic.utils import create_model_schema


class DynamicTestCase(TestCase):
    def test_tables_create(self):
        client = APIClient()
        response = client.post(
            "/api/table/",
            {
                "name": "test table",
                "columns": [
                    {"name": "column1", "type": "text"},
                    {"name": "column2", "type": "number"},
                ],
            },
            format="json",
        )
        self.assertEqual(DatabaseTable.objects.count(), 1)
        self.assertEqual(Column.objects.count(), 2)

    def test_tables_create_and_read(self):
        client = APIClient()
        columns = [
            {"name": "column1", "type": "text"},
            {"name": "column2", "type": "number"},
        ]
        response = client.post(
            "/api/table/",
            {"name": "testtable", "columns": columns},
            format="json",
        )
        app_label = __package__.rsplit(".", 1)[-1]
        Model = create_model_schema(
            name="testtable", fields=columns, app_label=app_label
        )
        self.assertEqual(Model.objects.count(), 0)

    def test_adding_row_and_retrieve(self):
        client = APIClient()
        columns = [
            {"name": "column1", "type": "text"},
            {"name": "column2", "type": "number"},
        ]
        response = client.post(
            "/api/table/",
            {"name": "testo", "columns": columns},
            format="json",
        )
        app_label = __package__.rsplit(".", 1)[-1]
        Model = create_model_schema(name="testo", fields=columns, app_label=app_label)
        self.assertEqual(Model.objects.count(), 0)
        client.post(
            f"/api/table/{response.data['id']}/row/",
            {"column1": "testoooo", "column2": 2},
            format="json",
        )
        self.assertEqual(Model.objects.count(), 1)
        self.assertEqual(Model.objects.first().column1, "testoooo")
        response = client.get(
            f"/api/table/{response.data['id']}/rows/",
            format="json",
        )
        self.assertEqual(response.data[0]["column1"], "testoooo")

    def test_update_columns(self):
        client = APIClient()
        columns = [
            {"name": "column1", "type": "text"},
            {"name": "column2", "type": "number"},
        ]
        response = client.post(
            "/api/table/",
            {"name": "testo", "columns": columns},
            format="json",
        )
        client.post(
            f"/api/table/{response.data['id']}/row/",
            {"column1": "testoooo", "column2": 2},
            format="json",
        )
        client.put(
            f"/api/table/{response.data['id']}/",
            {"name": "testo", "columns": [{"name": "column2", "type": "text"}]},
            format="json",
        )
        response = client.get(
            f"/api/table/{response.data['id']}/rows/",
            format="json",
        )
        self.assertTrue(isinstance(response.data[0]["column2"], str))

    def test_invalid_create_table(self):
        client = APIClient()
        columns = [
            {"name": "column1", "type": "sth"},
            {"name": "column2", "type": "number"},
        ]
        response = client.post(
            "/api/table/",
            {"name": "testo", "columns": columns},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_update_columns(self):
        client = APIClient()
        columns = [
            {"name": "column1", "type": "text"},
            {"name": "column2", "type": "number"},
        ]
        response = client.post(
            "/api/table/",
            {"name": "testo", "columns": columns},
            format="json",
        )
        response = client.put(
            f"/api/table/{response.data['id']}/",
            {"name": "testo", "columns": [{"name": "column2", "type": "sth"}]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
