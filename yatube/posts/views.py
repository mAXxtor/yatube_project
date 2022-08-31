from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from . import utils
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

CACHE_TTL=20


@cache_page(CACHE_TTL, key_prefix='index_page')
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
    if author!=request.user:
        following = Follow.objects.filter(
            user=request.user.id,
            author=author.id
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'profile_posts': profile_posts,
        'page_obj': utils.paginator(request, profile_posts),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
        files=request.FILES or None, instance=post)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.save()
    return redirect('posts:post_detail', post_id)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    followed_posts = Post.objects.filter(author__following__user=request.user)
    return render(
        request,
        'posts/follow.html',
        {'page_obj': utils.paginator(request, followed_posts)}
    )

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', author)
