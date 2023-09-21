from django.db import models
from django.contrib.auth.hashers import make_password

# class UserMan(models.Model):
#     user = models.CharField(max_length=100)
#     password = models.CharField(max_length=128)

#     def save(self, *args, **kwargs):
#         # Encode the password before saving
#         self.password = make_password(self.password)
#         super(UserMan, self).save(*args, **kwargs)

#     def __str__(self):
#         return self.user
