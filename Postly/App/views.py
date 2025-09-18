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
from django.template.loader import render_to_string
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

    
    def get_queryset(self):
        queryset = Post.objects.all().order_by("-created_at")
        category_slug = self.request.GET.get("category")

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["selected_category"] = self.request.GET.get("category", "")
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        request = self.request
        user = request.user if request.user.is_authenticated else None
        ip = self.get_client_ip()

        if not PostView.objects.filter(post=post, user=user, ip_address=ip).exists():
            PostView.objects.create(post=post, user=user, ip_address=ip)
            post.views = post.post_views.count()  # update total views
            post.save(update_fields=['views'])

        return post

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    

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
        messages.success(self.request, "Your post has been created")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("Users:login")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()   # 🔥 add this
        return context

class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Your post has been updated")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "You are not allowed to edit this post")
            return redirect(post.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()   # 🔥 add this
        return context

class PostDeleteView(DeleteView):
    model = Post
    template_name = "post_confirm_delete.html"
    success_url = reverse_lazy("App:post_list")

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, " You cannot delete this post")
            return redirect(post.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)


def filter_posts(request):
    category_slug = request.GET.get("category")
    posts = Post.objects.all().order_by("-created_at")

    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    html = render_to_string("App/_post_cards.html", {"posts": posts, "user": request.user})
    return JsonResponse({"html": html})

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
            messages.success(request, "Comment added ")
        else:
            print("Comment form errors:", form.errors)
            messages.error(request, f"Failed to add comment: {form.errors}")

    else:
        messages.error(request, "Invalid request method.")

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
def post_list_api(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def post_detail_api(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(author=request.user)  
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def category_list_api(request):
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
def add_comment_api(request, pk):
    post = get_object_or_404(Post, pk=pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(post=post, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def like_post_api(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        return Response({"message": "Unliked"}, status=status.HTTP_200_OK)

    return Response({"message": "Liked"}, status=status.HTTP_201_CREATED)