from django.shortcuts import render, get_object_or_404
from taggit.models import Tag
from django.core.mail import send_mail
from django.conf import settings
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Count


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    return render(request, 'blog/post/list.html', {
        'posts': object_list,
        'tag': tag
    })


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    # Similar posts (by shared tags)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id).distinct()

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'new_comment': new_comment,
            'comment_form': comment_form,
            'similar_posts': similar_posts
        }
    )


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\nComments: {cd['comments']}"

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )


def post_search(request):
    query = None
    results = []

    if 'query' in request.GET:
        query = request.GET.get('query')
        search_vector = SearchVector('title', 'body')
        search_query = SearchQuery(query)
        results = Post.published.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(rank__gte=0.3).order_by('-rank')

    return render(
        request,
        'blog/post/search.html',
        {
            'query': query,
            'results': results
        }
    )