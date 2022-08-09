from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Group, Post


def index(request):
    posts = Post.objects.all()[:settings.NUMBER_OF_POSTS]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:settings.NUMBER_OF_POSTS]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
