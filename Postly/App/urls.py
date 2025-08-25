from django.urls import path
from . import views

app_name = "App"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("create/", views.PostCreateView.as_view(), name="post_create"),
    path("<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("<slug:slug>/like/", views.like_post, name="like_post"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]

