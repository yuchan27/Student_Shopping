from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 增加學生驗證欄位
    is_student_verified = models.BooleanField(default=False, verbose_name="學生驗證")
    
    def __str__(self):
        return self.username