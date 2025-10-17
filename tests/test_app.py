import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200  # Successful GET of index.html
    assert "text/html" in response.headers["content-type"]

def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    # Check if we have our sample activities
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()

def test_signup_success(client):
    """Test successful activity signup"""
    activity_name = "Chess Club"
    test_email = "test@mergington.edu"
    
    # Make sure test email is not already registered
    if test_email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(test_email)
    
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {test_email} for {activity_name}"
    assert test_email in activities[activity_name]["participants"]

def test_signup_duplicate(client):
    """Test signing up an already registered student"""
    activity_name = "Chess Club"
    test_email = "duplicate@mergington.edu"
    
    # Register the test email first
    if test_email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(test_email)
    
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity(client):
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_success(client):
    """Test successful unregistration from activity"""
    activity_name = "Chess Club"
    test_email = "unregister@mergington.edu"
    
    # Register the test email first
    if test_email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(test_email)
    
    response = client.post(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {test_email} from {activity_name}"
    assert test_email not in activities[activity_name]["participants"]

def test_unregister_not_registered(client):
    """Test unregistering a student who isn't registered"""
    activity_name = "Chess Club"
    test_email = "notregistered@mergington.edu"
    
    # Make sure test email is not registered
    if test_email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(test_email)
    
    response = client.post(f"/activities/{activity_name}/unregister?email={test_email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()