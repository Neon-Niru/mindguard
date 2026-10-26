import os
import tempfile
import unittest
from unittest.mock import patch

os.environ["MINDGUARD_DEFER_APP"] = "1"

from app import create_app  # noqa: E402
from database.db import db  # noqa: E402
from models.assessment import BurnoutAssessment  # noqa: E402
from models.interview import InterviewSession  # noqa: E402
from models.planner import PlannerTask  # noqa: E402
from models.recovery_goal import RecoveryGoal  # noqa: E402

INTERVIEW_FACTS = {
    "sleep": {
        "hours": 5,
        "quality": "Poor",
        "rested": "Rarely",
        "consistency": "Irregular",
    },
    "academic_load": {"study_hours": 10, "homework_load": "Heavy"},
    "emotional_exhaustion": {"feeling_drained": "Always"},
    "stress": {"stress_frequency": "High", "stress_control": "Low"},
}


def _fake_process_message(message, state, tone="supportive"):
    state.setdefault("history", []).append(
        {"role": "student", "content": message}
    )
    state.setdefault("data", {}).update(INTERVIEW_FACTS)
    state["missing"] = []
    return {"complete": True, "data": state["data"], "state": state}


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        database_path = os.path.join(self.temp_dir, "test.db")

        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
            "RETURN_RESET_TOKEN": True,
            "CORS_ORIGINS": ["http://localhost:5173"],
        })
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def register(self, name="Test Student", email="test@example.com", password="secret123"):
        response = self.client.post("/api/register", json={
            "full_name": name,
            "email": email,
            "password": password,
        })
        return response

    def auth_headers(self, email="test@example.com", password="secret123", name=None):
        response = self.client.post("/api/login", json={
            "email": email,
            "password": password,
        })

        if response.status_code != 200:
            self.register(
                name=name or email.split("@")[0].title(),
                email=email,
                password=password,
            )
            response = self.client.post("/api/login", json={
                "email": email,
                "password": password,
            })

        token = response.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def create_user(self, name, email, password="secret123"):
        self.register(name=name, email=email, password=password)
        return self.auth_headers(email=email, password=password)

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def test_register_returns_token_and_user(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data["token"])
        self.assertEqual(data["user"]["email"], "test@example.com")
        self.assertNotIn("password", data["user"])

    def test_register_rejects_invalid_email(self):
        response = self.client.post("/api/register", json={
            "full_name": "Test",
            "email": "not-an-email",
            "password": "secret123",
        })
        self.assertEqual(response.status_code, 400)

    def test_register_rejects_short_password(self):
        response = self.client.post("/api/register", json={
            "full_name": "Test",
            "email": "short@example.com",
            "password": "123",
        })
        self.assertEqual(response.status_code, 400)

    def test_register_rejects_duplicate_email(self):
        self.register()
        response = self.register(name="Another")
        self.assertEqual(response.status_code, 409)

    def test_login_rejects_wrong_password(self):
        self.register()
        response = self.client.post("/api/login", json={
            "email": "test@example.com",
            "password": "wrong",
        })
        self.assertEqual(response.status_code, 401)

    def test_protected_route_requires_token(self):
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        self.assertEqual(
            self.client.get(
                "/api/me",
                headers={"Authorization": "Bearer nonsense"},
            ).status_code,
            401,
        )

    def test_me_returns_current_user(self):
        headers = self.auth_headers()
        response = self.client.get("/api/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["email"], "test@example.com")

    def test_update_profile(self):
        headers = self.auth_headers()
        response = self.client.put("/api/me", headers=headers, json={
            "full_name": "Updated Name",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["user"]["full_name"],
            "Updated Name",
        )

    def test_change_password(self):
        headers = self.auth_headers()

        response = self.client.post("/api/change-password", headers=headers, json={
            "current_password": "secret123",
            "new_password": "newsecret123",
        })
        self.assertEqual(response.status_code, 200)

        old_login = self.client.post("/api/login", json={
            "email": "test@example.com",
            "password": "secret123",
        })
        self.assertEqual(old_login.status_code, 401)

        new_login = self.client.post("/api/login", json={
            "email": "test@example.com",
            "password": "newsecret123",
        })
        self.assertEqual(new_login.status_code, 200)

    def test_change_password_rejects_wrong_current_password(self):
        headers = self.auth_headers()
        response = self.client.post("/api/change-password", headers=headers, json={
            "current_password": "wrong",
            "new_password": "newsecret123",
        })
        self.assertEqual(response.status_code, 401)

    def test_forgot_and_reset_password(self):
        self.register()
        response = self.client.post("/api/forgot-password", json={
            "email": "test@example.com",
        })
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["reset_token"]

        reset = self.client.post("/api/reset-password", json={
            "token": token,
            "password": "brandnew123",
        })
        self.assertEqual(reset.status_code, 200)

        login = self.client.post("/api/login", json={
            "email": "test@example.com",
            "password": "brandnew123",
        })
        self.assertEqual(login.status_code, 200)

    def test_forgot_password_does_not_leak_unknown_email(self):
        response = self.client.post("/api/forgot-password", json={
            "email": "missing@example.com",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"].startswith("If an account"), True)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def test_settings_defaults_and_save(self):
        headers = self.auth_headers()

        defaults = self.client.get("/api/settings", headers=headers).get_json()
        self.assertEqual(defaults["theme"], "dark")
        self.assertEqual(defaults["ai_tone"], "supportive")

        response = self.client.post("/api/settings", headers=headers, json={
            "theme": "light",
            "notification_weekly": True,
            "ai_tone": "direct",
            "privacy_settings": "shared",
        })
        self.assertEqual(response.status_code, 200)

        saved = self.client.get("/api/settings", headers=headers).get_json()
        self.assertEqual(saved["theme"], "light")
        self.assertTrue(saved["notification_weekly"])
        self.assertEqual(saved["ai_tone"], "direct")
        self.assertEqual(saved["privacy_settings"], "shared")

    def test_settings_reject_invalid_tone(self):
        headers = self.auth_headers()
        response = self.client.post("/api/settings", headers=headers, json={
            "ai_tone": "rude",
        })
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------
    # Planner
    # ------------------------------------------------------------------

    def test_planner_crud(self):
        headers = self.auth_headers()

        created = self.client.post("/api/planner", headers=headers, json={
            "title": "Take a walk",
            "priority": "High",
            "due_date": "2026-10-26",
        })
        self.assertEqual(created.status_code, 201)
        task_id = created.get_json()["task"]["task_id"]

        listed = self.client.get("/api/planner", headers=headers).get_json()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["title"], "Take a walk")

        updated = self.client.put(
            f"/api/planner/{task_id}",
            headers=headers,
            json={"completed": True},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertTrue(updated.get_json()["task"]["completed"])

        deleted = self.client.delete(f"/api/planner/{task_id}", headers=headers)
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(self.client.get("/api/planner", headers=headers).get_json(), [])

    def test_planner_rejects_invalid_priority(self):
        headers = self.auth_headers()
        response = self.client.post("/api/planner", headers=headers, json={
            "title": "Task",
            "priority": "Urgent",
        })
        self.assertEqual(response.status_code, 400)

    def test_planner_tasks_are_scoped_to_owner(self):
        owner = self.auth_headers()
        other = self.create_user("Other", "other@example.com")

        created = self.client.post("/api/planner", headers=owner, json={
            "title": "Private task",
        })
        task_id = created.get_json()["task"]["task_id"]

        self.assertEqual(
            self.client.put(
                f"/api/planner/{task_id}",
                headers=other,
                json={"completed": True},
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.delete(
                f"/api/planner/{task_id}",
                headers=other,
            ).status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Interview / assessment flow
    # ------------------------------------------------------------------

    @patch("routes.interview.process_message", side_effect=_fake_process_message)
    def test_interview_completes_and_creates_plan(self, _mock):
        headers = self.auth_headers()

        response = self.client.post("/api/interview", headers=headers, json={
            "message": "I sleep 5 hours, I study 10 hours and I feel drained.",
        })
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["complete"])
        self.assertEqual(payload["report"]["risk_level"], "High")

        dashboard = self.client.get("/api/dashboard", headers=headers).get_json()
        self.assertTrue(dashboard["has_assessment"])
        self.assertEqual(dashboard["risk_level"], "High")
        self.assertTrue(dashboard["recovery_goals"])

        report = self.client.get("/api/report", headers=headers)
        self.assertEqual(report.status_code, 200)
        self.assertTrue(report.get_json()["goals"])

        progress = self.client.get("/api/progress", headers=headers).get_json()
        self.assertEqual(len(progress["assessments"]), 1)

        planner = self.client.get("/api/planner", headers=headers).get_json()
        self.assertTrue(any(t["task_source"] == "ENGINE" for t in planner))

        second = self.client.post("/api/interview", headers=headers, json={
            "message": "More",
            "session_id": payload["session_id"],
        })
        self.assertEqual(second.status_code, 409)

    def test_interview_rejects_empty_message(self):
        headers = self.auth_headers()
        response = self.client.post("/api/interview", headers=headers, json={
            "message": "   ",
        })
        self.assertEqual(response.status_code, 400)

    def test_interview_rejects_overlong_message(self):
        headers = self.auth_headers()
        response = self.client.post("/api/interview", headers=headers, json={
            "message": "x" * 5000,
        })
        self.assertEqual(response.status_code, 400)

    @patch("routes.interview.process_message", return_value={
        "complete": False,
        "reply": "How has your sleep been?",
        "state": {"data": {}, "history": [], "missing": ["sleep"]},
    })
    def test_interview_returns_reply_and_session(self, _mock):
        headers = self.auth_headers()
        response = self.client.post("/api/interview", headers=headers, json={
            "message": "Hello",
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["complete"])
        self.assertTrue(data["session_id"])
        self.assertTrue(data["reply"])

    # ------------------------------------------------------------------
    # IDOR protection
    # ------------------------------------------------------------------

    def test_assessment_is_scoped_to_owner(self):
        headers = self.auth_headers()

        with self.app.app_context():
            session = InterviewSession(user_id=1, interview_status="Completed")
            db.session.add(session)
            db.session.flush()

            assessment = BurnoutAssessment(
                user_id=1,
                session_id=session.session_id,
                burnout_score=50,
                wellness_score=50,
                risk_level="Moderate",
            )
            db.session.add(assessment)
            db.session.commit()
            assessment_id = assessment.assessment_id

        self.assertEqual(
            self.client.get(
                f"/api/assessment/{assessment_id}",
                headers=headers,
            ).status_code,
            200,
        )

        other = self.create_user("Other", "other@example.com")
        self.assertEqual(
            self.client.get(
                f"/api/assessment/{assessment_id}",
                headers=other,
            ).status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Empty state
    # ------------------------------------------------------------------

    def test_empty_dashboard_and_progress(self):
        headers = self.auth_headers()

        dashboard = self.client.get("/api/dashboard", headers=headers).get_json()
        self.assertFalse(dashboard["has_assessment"])

        progress = self.client.get("/api/progress", headers=headers).get_json()
        self.assertEqual(progress["assessments"], [])
        self.assertEqual(progress["planner"]["total"], 0)

        self.assertEqual(
            self.client.get("/api/report", headers=headers).status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Account deletion
    # ------------------------------------------------------------------

    def test_delete_account_removes_data(self):
        headers = self.auth_headers()
        self.client.post("/api/planner", headers=headers, json={
            "title": "Task",
        })

        response = self.client.delete("/api/me", headers=headers, json={
            "password": "secret123",
        })
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.client.get("/api/me", headers=headers).status_code, 401)

        with self.app.app_context():
            self.assertEqual(PlannerTask.query.count(), 0)
            self.assertEqual(RecoveryGoal.query.count(), 0)

    def test_delete_account_requires_password(self):
        headers = self.auth_headers()
        response = self.client.delete("/api/me", headers=headers, json={})
        self.assertEqual(response.status_code, 400)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
