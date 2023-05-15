from rest_framework.routers import DefaultRouter

from dynamic.views import DynamicTablesViewSet

router = DefaultRouter()
router.register(r"table", DynamicTablesViewSet)
