from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .forms import *
from .serializer import *


class PostListView(ListView):
    model = Post
    template_name = "post_list.html"
    context_object_name = "posts"
    ordering = ["-created_at"]
    paginate_by = 10  


class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context["comments"] = post.comments.select_related("author") 
        context["comment_form"] = CommentForm()
        context["total_likes"] = post.total_likes()
        if self.request.user.is_authenticated:
            context["liked"] = Like.objects.filter(
                user=self.request.user, post=post
            ).exists()
        return context

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Your post has been created ")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:  
            return redirect("Users:login")
        return super().dispatch(request, *args, **kwargs)

class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post_form.html"

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "You are not allowed to edit this post ")
            return redirect(post.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

class PostDeleteView(DeleteView):
    model = Post
    template_name = "post_confirm_delete.html"
    success_url = reverse_lazy("App:post_list")

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "You cannot delete this post ")
            return redirect(post.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, "Comment added 💬")
        else:
            messages.error(request, "Failed to add comment ")
    return redirect(post.get_absolute_url())

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "liked": liked,
                "likes": post.likes.count()
            })

    return redirect("post_detail", pk=pk)


@api_view(['GET', 'POST'])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # auto set logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(author=request.user)  # keep user consistent
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(post=post, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:  # if already liked, unlike
        like.delete()
        return Response({"message": "Unliked"}, status=status.HTTP_200_OK)

    return Response({"message": "Liked"}, status=status.HTTP_201_CREATED)