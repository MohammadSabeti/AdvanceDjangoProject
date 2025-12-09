import re
from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Profile
from django.urls import reverse

# getting user model object
# User=get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Post(models.Model):
    class Meta:
        ordering = ['-created_date']


    author = models.ForeignKey(Profile, on_delete=models.SET_NULL,
                               null=True,related_name='posts_author')
    image = models.ImageField(upload_to='blog/',blank=True, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.BooleanField(default=False)
    category=models.ForeignKey('Category',on_delete=models.SET_NULL,
                               null=True,related_name='posts_category')

    published_date = models.DateTimeField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


    def first_sentence(self):
        if not self.content:
            return ''
        # Finding the first sentence based on . or ! or ?
        match = re.split(r'(?<=[.!؟])\s+', self.content.strip())
        return f'{match[0]} ...' if match else ''

    def get_absolute_api_url(self):
        return reverse("blog:api-v1:post-detail",
                       kwargs={"pk":self.pk})

    def __str__(self):
        return f'{self.id} - {self.title}'


