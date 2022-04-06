# posts/views.py
from django.shortcuts import render, get_object_or_404

from .models import Post, Group


# Главная страница
def index(request):    
    template = 'posts/index.html'
    title = 'Главная страница проекта'
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'title': title,
        'posts': posts,
    }    
    return render(request, template, context)

# Главная страница
# def group_list(request):    
#     template = 'posts/group_list.html'
#     return render(request, template)

# В url мы ждем параметр, и его передаем в функцию для использования
# def group_posts(request, slug):
#     return HttpResponse(f'Обработка запроса группы: {slug}')

# Страница с группами проекта Yatube
def group_posts(request, slug):    
    template = 'posts/group_list.html'
    text = 'Здесь будет информация о группах проекта Yatube'

    # Функция get_object_or_404 получает по заданным критериям объект 
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'title': text,
        'group': group,
        'posts': posts,
    }  
    return render(request, template, context)    