from django.db import models
from user.models import *
from topic.models import *
# Create your models here.

class Message(models.Model):
    content=models.CharField(max_length=50,verbose_name='內容')
    created_time=models.DateTimeField(auto_now_add=True,verbose_name='創建時間')
    publisher=models.ForeignKey(UserProfile)
    topic=models.ForeignKey(Topic)
    parent_message=models.IntegerField(default=0)

    class Meta:
        db_table='message'
