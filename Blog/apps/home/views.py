from django.http import HttpResponseNotFound
from django.views import View
from home.models import ArticleCategory, Article, Comment
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse


class IndexView(View):
    def get(self, request):
        cat_id = request.GET.get('cat_id', 1)
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 3)
        categories = ArticleCategory.objects.all()
        try:
            category = ArticleCategory.objects.get(id=cat_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('没有此分类')

        articles = Article.objects.filter(category=category)
        paginator = Paginator(articles, page_size)
        try:
            page_articles = paginator.page(page_num)
        except EmptyPage:
            # 如果没有分页数据，默认给用户404
            return HttpResponseNotFound('empty page')
        total_page = paginator.num_pages

        context = {
            'categories': categories,
            'category': category,
            'articles': page_articles,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, 'index.html', context=context)


class DetailView(View):

    def get(self, request):
        id = request.GET.get('id')
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 3)
        categories = ArticleCategory.objects.all()
        try:
            article = Article.objects.get(id=id)
        except Article.DoesNotExist:
            return render(request, '404.html')
        else:
            article.total_views += 1
            article.save()

        hot_articles = Article.objects.filter(category=article.category).order_by('-total_views')[:5]
        comments = Comment.objects.filter(article=article).order_by('-created')
        total_count = comments.count()
        paginator = Paginator(comments, page_size)
        try:
            page_comments = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        total_page = paginator.num_pages
        context = {
            'categories': categories,
            'category': article.category,
            'article': article,
            'hot_articles': hot_articles,
            'total_count': total_count,
            'comments': page_comments,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, 'detail.html', context=context)

    def post(self, request):
        user = request.user
        id = request.GET.get('id')
        if user and user.is_authenticated:
            id = request.POST.get('id')
            content = request.POST.get('content')
            try:
                article = Article.objects.get(id=id)
            except Article.DoesNotExist:
                return HttpResponseNotFound('没有此文章')
            Comment.objects.create(content=content, article=article, user=user)
            article.comments_count += 1
            article.save()
            path = reverse('home:detail') + '?id={}'.format(article.id)
            return redirect(path)
        else:
            return redirect(reverse('users:login') + "?next=" + reverse('home:detail') + '?id={}'.format(id))
