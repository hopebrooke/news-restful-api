from django.db import models
from django.contrib.auth.models import User


# Author model
class Author(models.Model):
    user = models.ForeignKey( User, on_delete = models.CASCADE)

    def __str__(self):
        return self.user.username
    
# Story model  
class Story(models.Model):
    headline = models.CharField(max_length=64)
    categoryTypes = [('pol', 'politics'), ('art', 'art'), ('tech', 'technology'), ('trivia', 'trivial')]
    category = models.CharField(max_length=6, choices=categoryTypes)
    regionTypes = [('uk', 'UK'), ('eu', 'EU'), ('w', 'World')]
    region = models.CharField(max_length=2, choices=regionTypes)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    date = models.DateField()
    details = models.CharField(max_length=128)
