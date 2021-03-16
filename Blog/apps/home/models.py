from django.db import models
from django.utils import timezone


class ArticleCategory(models.Model):
    title = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'tb_category'
        verbose_name = '类别管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Article(models.Model):
    author = models.ForeignKey("users.User", on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    # 文章栏目的 “一对多” 外键
    category = models.ForeignKey(ArticleCategory, null=True, blank=True,
                                 on_delete=models.CASCADE, related_name='article')
    tags = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=100, null=False, blank=False)
    sumary = models.CharField(max_length=200, null=False, blank=False)
    content = models.TextField()
    total_views = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering 指定模型返回的数据的排列顺序
        # '-created' 表明数据应该以倒序排列
        db_table = 'tb_article'
        ordering = ('-created',)
        verbose_name = '文章管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article.title

    class Meta:
        db_table = 'tb_comment'
        verbose_name = '评论管理'
        verbose_name_plural = verbose_name
