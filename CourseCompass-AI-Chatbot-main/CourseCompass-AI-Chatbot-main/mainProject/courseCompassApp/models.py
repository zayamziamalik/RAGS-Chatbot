from django.db import models

class User(models.Model):
    email = models.CharField(max_length=100,default='')
    messages = models.JSONField(default=list,blank=True)

    