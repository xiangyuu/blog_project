from django.db import models
from user.models import *
# Create your models here.
class Topic(models.Model):
    title=models.CharField(max_length=50,verbose_name='主題')
    category=models.CharField(max_length=20,verbose_name='類別')
    limit=models.CharField(max_length=10,verbose_name='權限')
    introduce=models.CharField(max_length=90,verbose_name='簡介')
    content=models.TextField(verbose_name='內容')
    created_time=models.DateTimeField(auto_now_add=True,verbose_name='創建時間')
    modified_time=models.DateTimeField(auto_now=True,verbose_name='修改時間')
    author=models.ForeignKey(UserProfile)

    class Meta:
        db_table='topic'