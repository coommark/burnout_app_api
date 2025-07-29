from locust import HttpUser, task, between
import random

class BurnoutUser(HttpUser):
    wait_time = between(1, 2)  # simulate user think time

    def on_start(self):
        # Called when a simulated user starts
        self.email = f"user{random.randint(1, 10000)}@test.com"
        self.password = "testpass"
        self.full_name = "Locust Test User"

        # Register user (ignore duplicate failures)
        self.client.post("/users/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": self.full_name
        })

        # Log in
        res = self.client.post("/users/login", data={
            "username": self.email,
            "password": self.password
        })
        try:
            self.token = res.json()["access_token"]
        except:
            self.token = None

        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(2)
    def submit_assessment(self):
        data = {
            "tired_score": random.randint(0, 6),
            "capable_score": random.randint(0, 6),
            "meaningful_score": random.randint(0, 6)
        }
        self.client.post("/assessments/", json=data, headers=self.headers)

    @task(1)
    def access_dashboard(self):
        self.client.get("/dashboard/", headers=self.headers)
