from django.urls import path, include
from rest_framework import routers
from app.views import *


router = routers.DefaultRouter()

router.register(r'sqlserverconns', SqlServerConnViewSet)
router.register(r'groupeditems', GroupedItemsViewSet)
router.register(r'issueitems', IssueItemViewSet)
router.register(r'persons', PersonSet)
router.register(r'labours', LabourViewSet)
router.register(r'customuoms', CustomUOMViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
