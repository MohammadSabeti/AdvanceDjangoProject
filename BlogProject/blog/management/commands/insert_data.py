from datetime import timedelta
from faker import Faker
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile, User
from blog.models import Category, Post

SEED = 52
USER_COUNT = 10

class Command(BaseCommand):
    help = "Insert test data (users, profiles, categories, posts) into database"

    def __init__(self,*args,**kwargs):
        super(Command,self).__init__(*args,**kwargs)
        self.fake = Faker()
        self.fake.seed_instance(SEED)  # deterministic per command run

    def handle(self, *args, **options):
        # =======================
        # Users
        # =======================

        user_emails=[self.fake.unique.safe_email() for _ in range(USER_COUNT)]
        users = []
        for email in user_emails:
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(email=email, password="TestPass123!")
            users.append(user)

        # clear Faker unique cache (good practice in long runs)
        self.fake.unique.clear()

        # =======================
        # Profiles
        # =======================
        descriptions = [
            "Full-stack developer with a strong interest in Django and scalable backend systems.",
            "Frontend engineer focused on clean UI, accessibility, and modern JavaScript frameworks.",
            "Backend developer experienced in APIs, databases, and performance optimization.",
            "DevOps enthusiast who enjoys automation, CI/CD pipelines, and cloud infrastructure.",
            "UI/UX designer passionate about human-centered design and product usability.",
            "Data scientist working with Python, machine learning models, and analytics.",
            "Security researcher interested in web vulnerabilities and secure coding practices.",
            "Mobile developer building cross-platform apps with a focus on performance.",
            "Technical writer who simplifies complex engineering topics for developers.",
            "Startup CTO with experience in leading engineering teams and system architecture.",
        ]


        profiles = []
        for user, desc in zip(users, descriptions):
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.first_name = self.fake.first_name()
            profile.last_name = self.fake.last_name()
            profile.description = desc
            profile.save()
            profiles.append(profile)

        # =======================
        # Categories (<= 20 chars)
        # =======================
        category_names = [
            "Tech",
            "Programming",
            "Security",
            "AI",
            "WebDev",
            "Data",
            "Cloud",
            "Mobile",
            "OpenSource",
            "Career",
        ]

        categories = []
        for name in category_names:
            category, _ = Category.objects.get_or_create(name=name)
            categories.append(category)

        # =======================
        # Posts
        # =======================
        posts_data = [
            (
                "Getting Started with Django",
                "Django is a powerful Python web framework that encourages rapid development and clean design. "
                "It provides built-in tools for authentication, admin panels, and ORM support. "
                "By learning Django, developers can focus more on business logic instead of boilerplate code.",
                True,
            ),
            (
                "Securing Your Web App",
                "Security is a critical concern in modern web applications. "
                "Django offers strong defaults like CSRF protection and secure password hashing. "
                "Understanding common vulnerabilities helps developers build safer systems.",
                True,
            ),
            (
                "Building REST APIs",
                "RESTful APIs are the backbone of modern applications. "
                "Django REST Framework simplifies serialization, authentication, and permissions. "
                "With DRF, building scalable APIs becomes significantly easier.",
                True,
            ),
            (
                "Why Databases Matter",
                "Databases play a central role in application performance and reliability. "
                "Choosing the right database affects scalability, maintenance, and cost. "
                "Developers should understand both relational and non-relational options.",
                False,
            ),
            (
                "Docker for Django",
                "Docker allows developers to package applications with their runtime environment. "
                "Using containers ensures consistency between development and production systems. "
                "Django projects greatly benefit from Docker-based workflows.",
                True,
            ),
            (
                "Git Best Practices",
                "Version control is essential for any software project. "
                "Git enables collaboration, history tracking, and safe experimentation. "
                "Mastering Git workflows improves both individual and team productivity.",
                True,
            ),
            (
                "Writing Clean Code",
                "Clean code is easier to read, test, and maintain. "
                "Python encourages readability through simple syntax and conventions. "
                "Writing clean code is a long-term investment for every developer.",
                True,
            ),
            (
                "Understanding Middleware",
                "Middleware acts as a bridge between requests and responses. "
                "Django middleware can handle authentication, logging, and caching. "
                "Proper use of middleware keeps code modular and maintainable.",
                True,
            ),
            (
                "Testing Django Apps",
                "Automated testing ensures that applications behave as expected. "
                "Django provides a robust testing framework out of the box. "
                "Tests reduce bugs and increase confidence during refactoring.",
                True,
            ),
            (
                "Careers in Tech",
                "The tech industry offers diverse career paths and opportunities. "
                "Continuous learning is key to long-term success. "
                "Developers who adapt quickly stay relevant in a fast-changing field.",
                True,
            ),
        ]

        created_count = 0
        for i, (title, content, status) in enumerate(posts_data):
            _, created = Post.objects.get_or_create(
                title=title,
                author= profiles[i % len(profiles)],
                content= content.strip(),
                status= status,
                category= categories[i % len(categories)],
                published_date= timezone.now() - timedelta(days=i),

            )
            created_count += int(created)

        self.stdout.write(self.style.SUCCESS("✅ All test data created successfully."))
        self.stdout.write(
            f"Users: {len(users)} | Profiles: {len(profiles)} | "
            f"Categories: {len(categories)} | New posts: {created_count}"
        )
