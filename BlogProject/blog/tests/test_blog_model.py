from django.test import TestCase
from django.utils import timezone
from accounts.models import Profile,User
from ..models import Category,Post

class TestPostModel(TestCase):

    def setUp(self):
        self.user=User.objects.create_user(email='test22@test.com',password='tesT1523678/')

        self.profile = self.user.profile
        self.profile.first_name = "test_first_name"
        self.profile.last_name = "test_last_name"
        self.profile.description = "test_description"
        self.profile.save()

        self.category = Category.objects.create(name='Bye Bye')

    def test_create_post_with_valid_data(self):

        post=Post.objects.create(title='test_title',content='test_content',
                                 author=self.profile,status=False,category=self.category,
                                 published_date=timezone.now())

        # self.assertEqual(post.title,'test_title')
        self.assertTrue(Post.objects.filter(pk=post.id).exists())