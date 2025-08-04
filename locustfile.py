# locustfile.py
from locust import HttpUser, task, between, events
from locust.exception import StopUser
from uuid import uuid4
import random

# -----------------------------
# SLA Configuration
# -----------------------------
SLA_P95_MS = 2000  # ≤ 2 seconds
# (method, endpoint name). Names must match the 'name=' given in requests below.
SLA_ENDPOINTS = [
    ("POST", "/assessments/"),
    ("GET", "/dashboard/"),
]


class BurnoutUser(HttpUser):
    """
    Simulated user flow:
      - Register (ignore duplicate)
      - Login and store Bearer token
      - Post daily assessment (weighted 2)
      - View dashboard (weighted 1)
    """
    wait_time = between(1, 2)  # simulate think time

    def on_start(self):
        # Generate a unique credential per simulated user
        self.email = f"user_{uuid4().hex[:12]}@test.com"
        self.password = "testpass"
        self.full_name = "Locust Test User"

        # Attempt registration (ignore duplicates or non-2xx)
        self.client.post(
            "/users/register",
            json={
                "email": self.email,
                "password": self.password,
                "full_name": self.full_name,
            },
            name="/users/register"
        )

        # Login (OAuth2 form-style)
        res = self.client.post(
            "/users/login",
            data={"username": self.email, "password": self.password},
            name="/users/login"
        )

        if res.status_code != 200:
            # Stop this user so it doesn't pollute results with unauthorized requests
            raise StopUser(f"Login failed (status {res.status_code})")

        try:
            token = res.json().get("access_token")
        except Exception:
            token = None

        if not token:
            raise StopUser("Login response missing access_token")

        self.headers = {"Authorization": f"Bearer {token}"}

    @task(2)
    def submit_assessment(self):
        """
        Submit a daily assessment. The backend should trigger prediction inside this path.
        """
        data = {
            "tired_score": random.randint(0, 6),
            "capable_score": random.randint(0, 6),
            "meaningful_score": random.randint(0, 6),
        }
        # Use 'name' to normalize stats grouping for SLA checks
        self.client.post(
            "/assessments/",
            json=data,
            headers=self.headers,
            name="/assessments/",
        )

    @task(1)
    def access_dashboard(self):
        """
        Retrieve dashboard, which should reflect latest risk/prediction.
        """
        self.client.get(
            "/dashboard/",
            headers=self.headers,
            name="/dashboard/",
        )


# -----------------------------
# SLA Gate at Test End
# -----------------------------
@events.quitting.add_listener
def _(environment, **kwargs):
    """
    Enforce SLA on key endpoints at the end of a headless run.
    Fails the process (non-zero exit) if any p95 > SLA_P95_MS.
    """
    stats = environment.stats
    all_ok = True
    lines = []
    lines.append("\n=== SLA REPORT (p95) ===")
    for method, name in SLA_ENDPOINTS:
        entry = stats.get(name, method)
        if not entry or entry.num_requests == 0:
            lines.append(f"{method} {name:<20} — no requests recorded")
            all_ok = False
            continue

        p95 = entry.get_response_time_percentile(0.95)
        fail_ratio = entry.fail_ratio
        lines.append(
            f"{method} {name:<20} p95={p95:.1f} ms | failures={entry.num_failures} ({fail_ratio:.2%})"
        )
        if p95 > SLA_P95_MS:
            all_ok = False

    # Also include an aggregate line for visibility (not enforced here)
    total_p95 = stats.total.get_response_time_percentile(0.95)
    lines.append(f"TOTAL (all requests)    p95={total_p95:.1f} ms | failures={stats.total.num_failures} ({stats.total.fail_ratio:.2%})")
    print("\n".join(lines))

    if not all_ok:
        print(f"\nSLA NOT MET: One or more endpoints exceeded p95 > {SLA_P95_MS} ms.")
        environment.process_exit_code = 1
    else:
        print(f"\nSLA MET: All monitored endpoints have p95 ≤ {SLA_P95_MS} ms.")
