import pytest
from app.auth import get_current_user
from app.main import app
from app.models import Candidate, User, Role


@pytest.fixture
def reviewer_user(session):
    user = User(email="reviewer@example.com", password="hashed_placeholder", role=Role.reviewer.value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def sample_candidate(session):
    candidate = Candidate(
        name="Jane Doe",
        email="jane@example.com",
        role_applied="Backend Engineer",
        skills=["Python", "FastAPI"],
        status="new",  # explicit — avoids relying on the model's "active" default,
                        # which isn't a valid CandidateStatus enum member
    )
    session.add(candidate)
    session.commit()
    session.refresh(candidate)
    return candidate


@pytest.fixture
def authed_client(client, reviewer_user):
    # Bypass real auth/JWT for these tests — inject the reviewer directly
    app.dependency_overrides[get_current_user] = lambda: reviewer_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


# 1. GET all candidates
def test_get_all_candidates(authed_client, sample_candidate):
    response = authed_client.get("/api/candidates")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    # CandidateListItem has no `email` field — assert on fields it does expose
    assert any(item["name"] == "Jane Doe" for item in data["items"])
    assert any(item["role_applied"] == "Backend Engineer" for item in data["items"])


# 2. GET candidate detail
def test_get_candidate_details(authed_client, sample_candidate):
    response = authed_client.get(f"/api/candidates/{sample_candidate.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["candidate"]["email"] == "jane@example.com"
    assert data["scores"] == []


# 3. POST a score for a candidate
def test_submit_score(authed_client, sample_candidate):
    payload = {
        "category": "Technical Skills",
        "score": 4,
        "note": "Strong problem solving",
    }
    response = authed_client.post(
        f"/api/candidates/{sample_candidate.id}/scores", json=payload
    )

    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "Technical Skills"