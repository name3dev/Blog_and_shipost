
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .models import Post, Comment, Like


def home(request):
    posts = Post.objects.all().order_by('-created_at')

    for post in posts:
        post.comments_preview = Comment.objects.filter(
            post=post
        ).select_related('author').order_by('-created_at')[:3]

        post.comments_count = Comment.objects.filter(post=post).count()

    return render(request, 'home.html', {
        'posts': posts
    })


def about(request):
    return HttpResponse("О нас")


def posts(request):
    all_posts = Post.objects.all().order_by('-created_at')

    return render(request, 'home.html', {
        'posts': all_posts
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')

    likes = Like.objects.filter(post=post, value=1).count()
    dislikes = Like.objects.filter(post=post, value=-1).count()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'likes': likes,
        'dislikes': dislikes
    })


@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        Post.objects.create(
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            author=request.user
        )

    return redirect('home')


@login_required(login_url='login')
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()

        return redirect('post_detail', post_id=post.id)

    comments = Comment.objects.filter(post=post).order_by('-created_at')

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'likes': Like.objects.filter(post=post, value=1).count(),
        'dislikes': Like.objects.filter(post=post, value=-1).count(),
        'edit_mode': True
    })


@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'post_detail.html', {
        'post': post,
        'delete_mode': True
    })


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'auth.html', {
                'auth_type': 'register',
                'error': 'Этот логин уже занят'
            })

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('login')

    return render(request, 'auth.html', {
        'auth_type': 'register'
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(request, 'auth.html', {
            'auth_type': 'login',
            'error': 'Неправильный логин или пароль'
        })

    return render(request, 'auth.html', {
        'auth_type': 'login'
    })


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content')

        if content and content.strip():
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )

    return redirect('post_detail', post_id=post.id)


@login_required(login_url='login')
def reaction(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        value = request.POST.get('value')

        if value in ['1', '-1']:
            value = int(value)

            like = Like.objects.filter(
                post=post,
                author=request.user
            ).first()

            if like:
                if like.value == value:
                    like.delete()
                else:
                    like.value = value
                    like.save()
            else:
                Like.objects.create(
                    post=post,
                    author=request.user,
                    value=value
                )

    return redirect('post_detail', post_id=post.id)
