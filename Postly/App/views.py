from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .models import Post, Comment, Like,Category
from .forms import PostForm, CommentForm
from django.utils import timezone


class PostListView(ListView):
    model = Post
    template_name = "post_list.html"
    context_object_name = "posts"
    ordering = ["-created_at"]


class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context["comments"] = post.comments.all()
        context["comment_form"] = CommentForm()
        context["total_likes"] = post.total_likes()
        if self.request.user.is_authenticated:
            context["liked"] = Like.objects.filter(user=self.request.user, post=post).exists()
        return context


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post_form.html"


class PostDeleteView(DeleteView):
    model = Post
    template_name = "post_confirm_delete.html"
    success_url = reverse_lazy("App:post_list")


@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect(post.get_absolute_url())


@login_required
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:  # Already liked → unlike
        like.delete()
    return HttpResponseRedirect(post.get_absolute_url())



def home(request):
    featured_posts = Post.objects.filter(featured=True).order_by('-published_date')[:3]
    latest_posts = Post.objects.all().order_by('-published_date')[:10]
    categories = Category.objects.all()
    recent_comments = Comment.objects.order_by('-created_at')[:5]

    return render(request, 'homepage.html', {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'categories': categories,
        'recent_comments': recent_comments,
    })
