# Postly/views.py
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from App.models import *
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Count

def home(request):
    query = request.GET.get("q")
    category_slug = request.GET.get("category")

    posts = Post.objects.all().order_by("-published_date")

    if query:
        posts = posts.filter(title__icontains=query)

    if category_slug:
        posts = posts.filter(category__slug=category_slug)
        
    posts = Post.objects.all().order_by("-published_date")
    paginator = Paginator(posts, 6) 
    page_number = request.GET.get('page')
    latest_posts = paginator.get_page(page_number)

    featured_posts = posts.filter(featured=True)[:3]
    latest_posts = posts[:10]
    categories = Category.objects.annotate(num_posts=Count('posts')).filter(num_posts__gt=0)
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
        print(f"Subscribed: {email}")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



@csrf_exempt
def increment_post_view(request, pk):
    """
    Increment post view via AJAX.
    Only counts unique views per user/IP.
    """
    post = get_object_or_404(Post, pk=pk)
    user = request.user if request.user.is_authenticated else None
    ip = get_client_ip(request)

    if not PostView.objects.filter(post=post, user=user, ip_address=ip).exists():
        PostView.objects.create(post=post, user=user, ip_address=ip)
        post.views = post.post_views.count()
        post.save(update_fields=['views'])

    return JsonResponse({'views': post.views})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
