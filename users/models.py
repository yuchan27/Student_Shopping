from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 增加學生驗證欄位
    is_student_verified = models.BooleanField(default=False, verbose_name="學生驗證")
    nickname = models.CharField(max_length=20, blank=True, verbose_name='暱稱')
    phone = models.CharField(max_length=10, blank=True, verbose_name='手機號碼')
    
    def __str__(self):
        return self.username