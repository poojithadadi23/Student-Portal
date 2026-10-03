from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register("profile", StudentProfileViewSet, basename="profile")

router.register("documents", DocumentViewSet, basename="documents")

urlpatterns = router.urls

urlpatterns += [

    path("conversation/ask/", conversation_ask, name="conversation_ask"),

    path("conversation/", create_conversation, name="create_conversation")

]
urlpatterns = router.urls




