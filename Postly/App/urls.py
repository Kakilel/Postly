from django.urls import path
from . import views

app_name = "App"

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/", views.PostListView.as_view(), name="post_list"),
    path("create/", views.PostCreateView.as_view(), name="post_create"),
    path("<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("<int:pk>/like/", views.like_post, name="like_post"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    
]
