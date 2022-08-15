from os import path

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm

POST_AMOUNT = 10


def get_page_obj(request, posts_list, posts_amount=POST_AMOUNT):
    """Получение страницы с постами от паджинатора."""

    paginator = Paginator(posts_list, posts_amount)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    """Главная страница проекта yatube."""

    template = path.join('posts', 'index.html')
    page_obj = get_page_obj(request, Post.objects.all())
    return render(request, template, {'page_obj': page_obj})


def group_posts(request, slug):
    """Страница с группами проекта Yatube."""

    template = path.join('posts', 'group_list.html')
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_page_obj(request, group.posts.all())
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Создание записи."""

    template = path.join('posts', 'create_post.html')
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        new_record = form.save(commit=False)
        new_record.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user.username)
    context = {
        'form': form,
        'username': request.user.username,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""

    template = path.join('posts', 'create_post.html')
    post = get_object_or_404(Post, pk=post_id)
    is_edit = 1
    if request.user == post.author:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        context = {
            'form': form,
            'is_edit': is_edit,
        }
        return render(request, template, context)
    return redirect('posts:post_detail', post_id=post_id)


def post_detail(request, post_id):
    """Детали поста."""

    length_title = 30
    template = path.join('posts', 'post_detail.html')
    post = get_object_or_404(Post, pk=post_id)
    title = f'Пост {post.text[:length_title]}'
    author = get_object_or_404(User, username=post.author.username)
    posts_list = Post.objects.filter(author__exact=author).all()
    context = {
        'title': title,
        'post': post,
        'posts_count': posts_list.count(),
        'form': CommentForm(),
        'comments': post.comments.all(),
    }
    return render(request, template, context)


def profile(request, username):
    """Профайл пользователя."""

    template = path.join('posts', 'profile.html')
    author = get_object_or_404(User, username=username)
    posts_list = Post.objects.filter(author__exact=author).all()
    posts_count = posts_list.count()
    page_obj = get_page_obj(request, posts_list)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count,
        'following': following
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария."""

    template = path.join('posts', 'post_detail.html')
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'comments': post.comments.all(),
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    """Страница с подписками на авторов."""

    template = path.join('posts', 'follow.html')
    posts_list = Post.objects.filter(
        author__following__user=request.user
    ).all()
    page_obj = get_page_obj(request, posts_list)
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписка на автора username."""

    author = get_object_or_404(User, username=username)
    user_is_follower = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if request.user != author and not user_is_follower:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора username."""

    author = get_object_or_404(User, username=username)
    follower_record = Follow.objects.filter(
        user=request.user,
        author=author
    )
    if follower_record.exists():
        follower_record.delete()
    return redirect('posts:profile', username=username)
