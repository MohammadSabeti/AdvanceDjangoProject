# -*- coding: utf-8 -*-
from datetime import timedelta

from django.utils import timezone

from accounts.models import Profile, User
from blog.models import Category, Post

# =======================
# Users
# =======================

user_emails = [
    "alice.johnson@example.com",
    "bob.smith@example.com",
    "carol.davis@example.com",
    "david.wilson@example.com",
    "emma.brown@example.com",
    "frank.miller@example.com",
    "grace.taylor@example.com",
    "henry.anderson@example.com",
    "irene.thomas@example.com",
    "jack.jackson@example.com",
]

users = []
for email in user_emails:
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_user(email=email, password="TestPass123!")
    users.append(user)

# =======================
# Profiles
# =======================

profile_data = [
    (
        "Alice",
        "Johnson",
        "Full-stack developer with a strong interest in Django and scalable backend systems.",
    ),
    (
        "Bob",
        "Smith",
        "Frontend engineer focused on clean UI, accessibility, and modern JavaScript frameworks.",
    ),
    (
        "Carol",
        "Davis",
        "Backend developer experienced in APIs, databases, and performance optimization.",
    ),
    (
        "David",
        "Wilson",
        "DevOps enthusiast who enjoys automation, CI/CD pipelines, and cloud infrastructure.",
    ),
    (
        "Emma",
        "Brown",
        "UI/UX designer passionate about human-centered design and product usability.",
    ),
    (
        "Frank",
        "Miller",
        "Data scientist working with Python, machine learning models, and analytics.",
    ),
    (
        "Grace",
        "Taylor",
        "Security researcher interested in web vulnerabilities and secure coding practices.",
    ),
    (
        "Henry",
        "Anderson",
        "Mobile developer building cross-platform apps with a focus on performance.",
    ),
    (
        "Irene",
        "Thomas",
        "Technical writer who simplifies complex engineering topics for developers.",
    ),
    (
        "Jack",
        "Jackson",
        "Startup CTO with experience in leading engineering teams and system architecture.",
    ),
]

profiles = []
for user, data in zip(users, profile_data):
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.first_name = data[0]
    profile.last_name = data[1]
    profile.description = data[2]
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

for i, data in enumerate(posts_data):
    Post.objects.get_or_create(
        title=data[0],
        defaults={
            "author": profiles[i % len(profiles)],
            "content": data[1].strip(),
            "status": data[2],
            "category": categories[i % len(categories)],
            "published_date": timezone.now() - timedelta(days=i),
        },
    )

print("✅ All test data created successfully.")
