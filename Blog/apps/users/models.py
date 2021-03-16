from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField(max_length=20, unique=True, blank=False)
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    user_desc = models.TextField(max_length=500, blank=True)
    USERNAME_FIELD = 'mobile'  # 修改认证的字段
    REQUIRED_FIELDS = ['username', 'email']  # 创建超级管理员的需要必须输入的字段

    class Meta:
        db_table = 'tb_user'  # 修改默认的表名
        verbose_name = '用户信息'  # Admin后台显示
        verbose_name_plural = verbose_name  # Admin后台显示

    def __str__(self):
        return self.mobile
