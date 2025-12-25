from django.test import Client, TestCase
from django.urls import reverse, resolve
from django.utils import timezone
from accounts.models import Profile,User
from ..models import Category,Post

class TestBlogView(TestCase):

    def setUp(self):
        self.client = Client()

        self.user=User.objects.create_user(email='test22@test.com',password='tesT1523678/')

        self.profile = self.user.profile
        self.profile.first_name = "test_first_name"
        self.profile.last_name = "test_last_name"
        self.profile.description = "test_description"
        self.profile.save()

        self.category = Category.objects.create(name='Bye Bye')

        self.post = Post.objects.create(title='test_title', content='test_content',
                                   author=self.profile, status=False, category=self.category,
                                   published_date=timezone.now())

    def test_blog_index_url_successful_response(self):
        url=reverse('blog:index')
        response=self.client.get(url)

        self.assertEqual(response.status_code,200)
        # self.assertTrue(str(response.content).find('index'))
        self.assertContains(response, "index")
        self.assertTemplateUsed(response,'index.html')

    def test_blog_post_detail_logged_in_response(self):
        self.client.force_login(self.user)
        url = reverse('blog:post-detail-tmp', kwargs={'pk':  self.post.id})
        response=self.client.get(url)
        self.assertEqual(response.status_code,200)

    def test_blog_post_detail_anonymouse_response(self):
        url = reverse('blog:post-detail-tmp', kwargs={'pk':  self.post.id})
        response=self.client.get(url)
        self.assertEqual(response.status_code,302)