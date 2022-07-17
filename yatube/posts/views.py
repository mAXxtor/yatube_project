from django.http import HttpResponse
from django.shortcuts import render

# Главная страница.
def index(request):
    template = 'posts/index.html'
    title = 'Это главная страница проекта Yatube'
    context = {
        'title': title
    }
    return render(request, template, context)


# Страница с группами.
def group_list(request):
    template = 'posts/group_list.html'
    title = 'Здесь будет информация о группах проекта Yatube'
    context = {
        'title': title
    }
    return render(request, template, context)


# Страница с постами, отфильтрованными по группам.
def group_posts(request, slug):
    return HttpResponse(f'Здесь будут посты, отфильтрованные по группам. Например сейчас запрос был по группе {slug}')
