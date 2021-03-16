from django.db import models


class BaseModel(models.Model):
    # add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        abstract = True
