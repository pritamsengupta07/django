# models.py
from django.db import models
from django.contrib.auth.models import User

class LoginData(models.Model):
    username = models.CharField(max_length=255)
    success = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {'Successful' if self.success else 'Failed'}"





class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.created_at}'