from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "App"

urlpatterns = [
    path("posts/", views.PostListView.as_view(), name="post_list"),
    path("create/", views.PostCreateView.as_view(), name="post_create"),
    path("<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("<int:pk>/like/", views.like_post, name="like_post"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("filter-posts/",views.filter_posts, name="filter_posts"),
    
    #API paths
    path("api/categories/", views.category_list_api, name="api_category_list"),
    path("api/posts/", views.post_list_api, name="api_post_list"),
    path("api/posts/<int:pk>/", views.post_detail_api, name="api_post_detail"),
    path("api/posts/<int:post_id>/like/", views.like_post_api, name="api_like_post"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
