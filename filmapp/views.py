from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Blog
from .forms import BlogForm, RegistrationForm, ContactForm, CommentForm
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import CommentForm


def home(request):
    # Retrieve all blog posts
    all_blogs = Blog.objects.all().order_by('-created_at')

    # Set the number of blog posts to display per page
    blogs_per_page = 3

    # Create a Paginator instance
    paginator = Paginator(all_blogs, blogs_per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the Page object for the current page
    page = paginator.get_page(page_number)

    return render(request, 'filmapp/home.html', {'page': page})

def admin_posts(request):
    # Retrieve only admin blog posts
    admin_blogs = Blog.objects.filter(author__is_superuser=True).order_by('-created_at')

    # Set the number of blog posts to display per page
    blogs_per_page = 3

    # Create a Paginator instance
    paginator = Paginator(admin_blogs, blogs_per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the Page object for the current page
    page = paginator.get_page(page_number)

    return render(request, 'filmapp/admin_posts.html', {'page': page})



def guest_posts(request):
    # Retrieves only guests' blogs
    guest_posts = Blog.objects.filter(author__is_superuser=False).order_by('-created_at')

    blogs_per_page = 3

    paginator = Paginator(guest_posts, blogs_per_page)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)

    return render(request, 'filmapp/guest_posts.html', {'page': page})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():  
            form.save()  # Save the form data to the database
            return redirect("filmapp:login")  # Redirect to a success page or URL

    else:
        form = ContactForm()

    return render(request, 'filmapp/contact.html', {'form': form})

@login_required(login_url='filmapp:login')  # Add this decorator to require authentication.
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user  # Assign the logged in user as the author
            blog.save()
            return redirect('filmapp:home')
    else:
        form = BlogForm()
    
    return render(request, 'filmapp/create_blog.html', {'form': form})


def register(request):
    form = RegistrationForm()
    password_errors = None

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('filmapp:login')
        else:
            password_errors = form.errors.get('password1')

    return render(request, 'filmapp/auth/register.html', {'form': form})


def login_view(request):
    form = AuthenticationForm()
    password_errors = None

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('filmapp:home') 
        else:
            password_errors = form.errors.get('password')

    return render(request, 'filmapp/auth/login.html', {'form': form, 'password_errors': password_errors})

def logout_user(request):
    logout(request)
    return redirect('filmapp:login')

def blog_details(request, pk):
    blog = Blog.objects.get(pk=pk)
    return render(request, "filmapp/blog_details.html", {"blog": blog})

def search(request):
    query = request.GET.get('q')  # Get the search query from the request's GET parameters
    results = []

    if query:
        # Modify the search query to look for partial matches in both 'title' and 'content'
        results = Blog.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))

    return render(request, 'filmapp/search_results.html', {'query': query, 'results': results})

def author_posts(request, author_id):
    author = get_object_or_404(User, id=author_id)  # Retrieve the author by their User ID
    author_posts = Blog.objects.filter(author=author)

    return render(request, 'filmapp/author_posts.html', {'author': author, 'author_posts': author_posts})


def blog_details(request, pk):
    blog = Blog.objects.get(pk=pk)
    comment_form = CommentForm()  # Create an instance of the CommentForm

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog = blog
            comment.user = request.user  # Assuming users are logged in when commenting
            comment.save()
            return redirect('filmapp:blog_details', pk=pk)

    return render(request, "filmapp/blog_details.html", {"blog": blog, "comment_form": comment_form})


def add_comment(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog = blog
            comment.user = request.user  # Assuming users are logged in when commenting
            comment.save()
            return redirect('filmapp:blog_details', pk=pk)
    else:
        return redirect('filmapp:blog_details', pk=pk)  # Redirect back to blog details if the form is invalid


def edit_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('filmapp:blog_details', pk=pk)
    else:
        form = BlogForm(instance=blog)

    return render(request, 'filmapp/edit_blog.html', {'form': form, 'blog': blog})


def delete_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if request.method == 'POST':
        blog.delete()
        return redirect('filmapp:home')  # Redirect to the home page after deleting the blog

    return render(request, 'filmapp/delete_blog.html', {'blog': blog})




