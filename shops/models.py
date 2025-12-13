from django.db import models
from django.conf import settings

class Shop(models.Model):
    # 綁定使用者，一人一店
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shop')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name