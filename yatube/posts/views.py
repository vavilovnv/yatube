# posts/views.py
from django.shortcuts import render, HttpResponse


# Главная страница
def index(request):    
    return HttpResponse('Главная страница posts')

# В url мы ждем параметр, и его передаем в функцию для использования
def group_posts(request, slug):
    return HttpResponse(f'Обработка запроса группы: {slug}')