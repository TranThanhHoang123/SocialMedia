from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')  # Specify the basename here
router.register(r'post', views.PostViewSet, basename='post')  # Specify the basename here
router.register(r'comment', views.CommentViewSet, basename='comment')  # Specify the basename here

urlpatterns = [
    path('', include(router.urls)),

]