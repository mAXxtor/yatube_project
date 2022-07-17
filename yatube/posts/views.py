from django.http import HttpResponse
from django.shortcuts import render

# Главная страница.
def index(request):
    template = 'posts/index.html'
    return render(request, template) 


# Страница с постами, отфильтрованными по группам.
def group_posts(request, slug):
    return HttpResponse(f'Здесь будут посты, отфильтрованные по группам. Например сейчас запрос был по группе {slug}')
