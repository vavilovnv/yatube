# posts/urls.py
from django.urls import path

from . import views

# namespace
app_name = 'posts'

urlpatterns = [
    path('', views.index, name='posts_index'),
    path('group_list.html/', views.group_posts, name='group_list'),
] 