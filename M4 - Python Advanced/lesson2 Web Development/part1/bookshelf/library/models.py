from django.db import models
from django.contrib.auth import get_user_model

class Book(models.Model):
    STATUS_CHOICES = [
        ("to_read", "To Read"),
        ("reading", "Reading"),
        ("read", "Read"),
    ]
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=120)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="to_read")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"
