from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Blog
from django.core.paginator import Paginator


def home(request):
    # Retrieve all blog posts
    all_blogs = Blog.objects.all().order_by('-created_at')

    return render(request, 'filmapp/home.html', {'all_blogs': all_blogs})
