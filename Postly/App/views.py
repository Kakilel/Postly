from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse

from .models import Post, Comment, Like, Category
from .forms import PostForm, CommentForm


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




def home(request):
    query = request.GET.get("q")  # search query
    category_slug = request.GET.get("category")  # selected category

    featured_posts = Post.objects.filter(featured=True).order_by("-published_date")[:3]
    posts = Post.objects.all().order_by("-published_date")  # we'll filter this
    categories = Category.objects.all()
    recent_comments = Comment.objects.select_related("post", "author").order_by("-created_at")[:5]

    selected_category = None

    if query:
        posts = posts.filter(title__icontains=query) | posts.filter(content__icontains=query)

    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=selected_category)

    return render(request, "homepage.html", {
        "featured_posts": featured_posts,
        "latest_posts": posts[:10],  # filtered latest posts
        "categories": categories,
        "recent_comments": recent_comments,
        "selected_category": selected_category,
        "query": query,
    })

