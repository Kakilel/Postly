# Postly/views.py
from django.utils import timezone
from App.models import Post, Category, Comment
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST


def home(request):
    featured_posts = Post.objects.filter(featured=True).order_by('-created_at')[:3]
    latest_posts = Post.objects.all().order_by('-created_at')[:10]
    categories = Category.objects.all()
    recent_comments = Comment.objects.order_by('-created_at')[:5]

    return render(request, 'home.html', {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'categories': categories,
        'recent_comments': recent_comments,
        'now': timezone.now(),
    })
# Postly/views.py

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
