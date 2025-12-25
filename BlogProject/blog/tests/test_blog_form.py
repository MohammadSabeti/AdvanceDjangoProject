from django.test import SimpleTestCase,TestCase
from django.utils import timezone

from ..forms import PostForm
from ..models import Category

class TestPostForm(TestCase):
    # With test database => TestCase
    def test_post_form_with_valid_data(self):
        category_obj=Category.objects.create(name='Bye Bye')
        form=PostForm(data={
            'title':'test',
            'content':'description test ',
            'status':False,
            'category':category_obj,
            'published_date':timezone.now()
        })
        self.assertTrue(form.is_valid())

    def test_post_form_with_no_data(self):
        form=PostForm(data={})
        self.assertIn("title", form.errors)
        self.assertIn("content", form.errors)
        self.assertFalse(form.is_valid())
