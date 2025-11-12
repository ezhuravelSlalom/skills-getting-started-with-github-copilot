"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly games",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ethan@mergington.edu", "ava@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lily@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and produce school plays and performances",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["chloe@mergington.edu", "jack@mergington.edu"]
        },
        "Mathletes": {
            "description": "Compete in math competitions and solve challenging problems",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["oliver@mergington.edu", "ella@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "grace@mergington.edu"]
        }
    })


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Verify structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_registered(self, client):
        """Test signing up when already registered"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_full(self, client):
        """Test signing up when activity is full"""
        # Fill up Chess Club (max 12 participants, currently has 2)
        for i in range(10):
            client.post(
                f"/activities/Chess Club/signup?email=student{i}@mergington.edu"
            )
        
        # Try to add one more
        response = client.post(
            "/activities/Chess Club/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400
        assert "Activity is full" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successfully unregistering from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregistering when not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_redirects(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""

    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Programming Class"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify participant added
        after_signup = client.get("/activities")
        after_signup_count = len(after_signup.json()[activity]["participants"])
        assert after_signup_count == initial_count + 1
        assert email in after_signup.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify participant removed
        after_unregister = client.get("/activities")
        after_unregister_count = len(after_unregister.json()[activity]["participants"])
        assert after_unregister_count == initial_count
        assert email not in after_unregister.json()[activity]["participants"]

    def test_multiple_signups_different_activities(self, client):
        """Test signing up for multiple different activities"""
        email = "multiactivity@mergington.edu"
        
        # Sign up for multiple activities
        activities_to_join = ["Chess Club", "Programming Class", "Art Workshop"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify presence in all activities
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
