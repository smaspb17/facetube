
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required  # встр. авториз
from django.core.paginator import Paginator

from .models import Post, Group, Comment, Follow
from . forms import PostForm, CommentForm


SELECT_LIMIT = 10


def paginator(request, posts):
    paginator = Paginator(posts, SELECT_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all().select_related('author')
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    user = request.user
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group', 'author')
    page_obj = paginator(request, posts)
    post_count = author.posts.select_related('group', 'author').count()
    follower_count = Follow.objects.filter(user=user).count()
    following = (
        user.is_authenticated
        and Follow.objects.filter(user=user, author=author)
    )
    context = {
        'post_count': post_count,
        'page_obj': page_obj,
        'username': author,
        'posts': posts,
        'following': following,
        'follower_count': follower_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    username = post.author
    post_list = post.author.posts
    post_count = post_list.count()
    title = f' Пост {post.text[:30]}'
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        'post': post,
        'post_count': post_count,
        'title': title,
        'username': username,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        temp_form = form.save(commit=False)
        temp_form.author = request.user
        temp_form.save()
        return redirect(
            'posts:profile', temp_form.author
        )
    return render(request, template, {'form': form})


@login_required  # декоратор авторизации
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,  # добавление изображений
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, template,
                  {'form': form, 'is_edit': True,
                   'post': post})


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    # Получите пост и сохраните его в переменную post.
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # Страница подписок
    template = 'posts/follow.html'
    user = request.user
    post_list = Post.objects.filter(
        author__following__user=user
    )
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user:
        user.follower.get_or_create(
            user=user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    user = request.user
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=user,
        author=author
    )
    follow.delete()
    return redirect('posts:profile', username)
