# Postly/views.py
from django.utils import timezone
from App.models import Post, Category, Comment
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST


def home(request):
    query = request.GET.get("q")
    category_slug = request.GET.get("category")

    posts = Post.objects.all().order_by("-published_date")

    if query:
        posts = posts.filter(title__icontains=query)

    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    featured_posts = posts.filter(featured=True)[:3]
    latest_posts = posts[:10]
    categories = Category.objects.all()
    recent_comments = Comment.objects.select_related("post", "author").order_by("-created_at")[:5]

    return render(request, "home.html", {
        "featured_posts": featured_posts,
        "latest_posts": latest_posts,
        "categories": categories,
        "recent_comments": recent_comments,
        "selected_category": category_slug,
    })


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        print(f"Message from {name} ({email}): {subject} - {message}")
        return redirect('home')  # redirect after submission

    return render(request, 'contact.html', {'now': timezone.now()})

@require_POST
def newsletter_subscribe(request):
    email = request.POST.get("email")
    if email:
        # Save email to database or send to a service
        print(f"Subscribed: {email}")  # Replace with your actual logic
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
