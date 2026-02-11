from locust import HttpUser, task, between
import random
import uuid

API_PREFIX = "/api/v1"


class TestUser(HttpUser):
    wait_time = between(0.5, 2.0)  # think time شبیه انسان

    def on_start(self):
        self.token = None
        self.post_ids = []
        self.category_names = []

        user_info = {
            "email": "mohammadi.tik@gmail.com",
            "password": "1523612mA!"
        }

        # Login and set token

        # Approach 1
        with self.client.post(
                f"{API_PREFIX}/accounts/auth/jwt/create/", json=user_info,
                name="AUTH /jwt/create", catch_response=True, ) as resp:

            if resp.status_code != 200:
                resp.failure(f"Login failed: {resp.status_code} - {resp.text[:200]}")
                return

            data = resp.json()
            token = data.get("access")
            if not token:
                resp.failure("Login response missing 'access' token")
                return

            self.token = token
            resp.success()

        # Approach 2
        '''
        response=self.client.post(f'{API_PREFIX}/accounts/auth/jwt/create/',json=data, name="POST /jwt/create")
        response.raise_for_status()
        token = response.json().get("access",None)
        self.client.headers.update({'Authorization': f'Bearer {token}'})
        '''

        # 2) Warm up: fetch categories + initial post list
        self._load_categories()
        self._load_post_ids()

    def _auth_headers(self):
        # If token missing, requests will likely fail; we keep it explicit.
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _load_categories(self):
        with self.client.get(
                f"{API_PREFIX}/blog/category/",
                headers=self._auth_headers(),
                name="GET /categories (warmup)",
                catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Category fetch failed: {resp.status_code}")
                return

            data = resp.json()
            self.category_names = [c["name"] for c in data if "name" in c]
            resp.success()

    def _load_post_ids(self):
        with self.client.get(
                f"{API_PREFIX}/blog/post/?page=1",
                headers=self._auth_headers(),
                name="GET /posts (warmup)",
                catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Post list warmup failed: {resp.status_code}")
                return

            data = resp.json()
            results = data.get("results", [])
            self.post_ids = [p["id"] for p in results if "id" in p]
            resp.success()

    @task(6)
    def get_post_list(self):
        self.client.get(f"{API_PREFIX}/blog/post/", headers=self._auth_headers(), name="GET /posts")

    @task(2)
    def post_detail(self):
        if self.post_ids:
            post_id = random.choice(self.post_ids)
        else:
            post_id = random.randint(41, 50)
        self.client.get(f"{API_PREFIX}/blog/post/{post_id}/", headers=self._auth_headers(), name="GET /posts/:id")

    @task(1)
    def create_post(self):
        category_name = random.choice(self.category_names) if self.category_names else None
        payload = {
            "title": f"Load test post {uuid.uuid4().hex[:8]}",
            "content": "Hello from locust",
            "status": random.choice([True,False]),
            "category": category_name,
            "published_date": "2026-02-10T16:50:42.630Z",
        }

        with self.client.post(
                f"{API_PREFIX}/blog/post/",
                json=payload,
                headers=self._auth_headers(),
                name="POST /posts",
                catch_response=True,
        ) as resp:
            # If a permission / validation error occurs, it should be noted in the report
            if resp.status_code not in (200, 201):
                resp.failure(f"Create failed: {resp.status_code} - {resp.text[:200]}")
                return
            resp.success()


    @task(2)
    def get_post_category_list(self):
        self.client.get(
            f"{API_PREFIX}/blog/category/",
            headers=self._auth_headers(),
            name="GET /categories",
        )
