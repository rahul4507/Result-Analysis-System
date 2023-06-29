from django.db import models

from user.models import CustomUser


# Create your models here.
class HOD(models.Model):
    name = models.CharField(max_length=32)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'HOD: {self.user}'
