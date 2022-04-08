# posts/views.py
from django.shortcuts import render, get_object_or_404

from .models import Post, Group


POSTS_AMOUNT = 10


# Главная страница
def index(request):
    template = 'posts/index.html'
    title = 'Главная страница проекта'
    posts = Post.objects.all()[:POSTS_AMOUNT]
    print(Post.objects)
    context = {
        'title': title,
        'posts': posts,
    }
    return render(request, template, context)


# Страница с группами проекта Yatube
def group_posts(request, slug):
    template = 'posts/group_list.html'
    text = 'Здесь будет информация о группах проекта Yatube'
    group = get_object_or_404(Group, slug=slug)
    posts = group.post_set.all()[:POSTS_AMOUNT]
    context = {
        'title': text,
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)


# Не используется
def group_list(request):
    template = 'posts/group_list.html'
    return render(request, template)
