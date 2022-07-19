from django.shortcuts import render, get_object_or_404
from .models import Post, Group

# Главная страница.
def index(request):
    title = 'Это главная страница проекта Yatube'
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'title': title,
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


# Страница с группами.
def group_list(request):
    title = 'Информация о группах проекта Yatube'
    context = {
        'title': title
    }
    return render(request, 'posts/group_list.html', context)


# Страница с постами, отфильтрованными по группам.
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = (f'Посты группы {slug}')
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'title': title,
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
