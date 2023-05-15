from django.test import TestCase
from rest_framework.test import APIClient

from dynamic.models import Column, DatabaseTable


class DynamicTestCase(TestCase):

    def test_tables_create(self):
        client = APIClient()
        response = client.post(
            "/api/table/",
            {"name": "test table", "columns": [
                {"name": "column1", "type": "text"},
                {"name": "column2", "type": "number"}
            ]},
            format="json",
        )
        self.assertEqual(DatabaseTable.objects.count(), 1)
        self.assertEqual(Column.objects.count(), 2)
