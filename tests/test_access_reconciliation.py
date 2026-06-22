from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_reconcile_access_returns_expected_grants_revokes_and_matches():
    response = client.post(
        "/access/reconcile",
        json={
            "system_access_list": ["alice", "bob", "charlie"],
            "database_access_list": ["bob", "dana", "erin"],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "grant_system_access": ["dana", "erin"],
        "revoke_system_access": ["alice", "charlie"],
        "matched_access": ["bob"],
    }


def test_reconcile_access_deduplicates_and_sorts_lists():
    response = client.post(
        "/access/reconcile",
        json={
            "system_access_list": ["zoe", "amy", "amy"],
            "database_access_list": ["amy", "mia", "mia"],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "grant_system_access": ["mia"],
        "revoke_system_access": ["zoe"],
        "matched_access": ["amy"],
    }
