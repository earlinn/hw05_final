from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

RECORDS_NUMBER_PER_PAGE = 10
User = get_user_model()


def paginator(request, object_list, per_page):
    paginate = Paginator(object_list, per_page)
    page_number = request.GET.get('page')
    page_obj = paginate.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginator(request, post_list, RECORDS_NUMBER_PER_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(request, post_list, RECORDS_NUMBER_PER_PAGE)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.all()
    following = False
    if request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=user
    ).exists():
        following = Follow.objects.get(user=request.user, author=user)
    page_obj = paginator(request, user_posts, RECORDS_NUMBER_PER_PAGE)
    context = {
        'author': user,
        'following': following,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        edited_post = form.save(commit=False)
        edited_post.author = request.user
        edited_post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    author_list = [follow.author for follow in request.user.follower.all()]
    post_list = Post.objects.filter(author__in=author_list)
    page_obj = paginator(request, post_list, RECORDS_NUMBER_PER_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user=request.user, author=author).exists()
    if author != request.user and not following:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user=request.user, author=author).exists()
    if following:
        following_object = Follow.objects.get(user=request.user, author=author)
        following_object.delete()
    return redirect('posts:profile', username)
