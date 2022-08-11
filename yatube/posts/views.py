from django.contrib.auth. decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render


from . import utils
from .forms import PostForm
from .models import Group, Post, User


def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    context = {'page_obj': utils.paginator(request, posts)}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    context = {
        'group': group,
        'page_obj': utils.paginator(request, posts)
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, author):
    author = get_object_or_404(User, username=author)
    profile_posts = author.posts.select_related('group')
    context = {
        'author': author,
        'page_obj': utils.paginator(request, profile_posts)
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid() or request.method == 'GET':
        form = PostForm()
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST, instance=post)
    if not post.author == request.user:
        return redirect('posts:post_detail', post_id)
    if not form.is_valid() or request.method == 'GET':
        form = PostForm(instance=post)
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save()
    return redirect('posts:post_detail', post_id)
