import pytest

from flask import g

from db_models import Sourcedir, Sourcefile
from tests.fixtures_for_tests import TEST_TARGET_LANGUAGE_CODE
from tests.backend.utils_for_testing import build_url_with_query
from views.sourcefile_api import generate_sourcefile_api


def _auth_ok():
    # Minimal stub user/profile for the auth decorator
    g.user = {"id": "test-user", "email": "test@example.com"}
    g.user_id = "test-user"
    class P:  # simple non-None profile object
        pass
    g.profile = P()
    return True


def _auth_fail():
    g.user = None
    g.user_id = None
    g.profile = None
    return False


def test_generate_requires_auth(monkeypatch, client):
    # Force auth failure
    monkeypatch.setattr("utils.auth_utils._attempt_authentication_and_set_g", _auth_fail)

    url = build_url_with_query(
        client,
        generate_sourcefile_api,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )

    resp = client.post(url, json={})
    assert resp.status_code == 401


def test_generate_happy_path(monkeypatch, fixture_for_testing_db, client):
    # Authenticate
    monkeypatch.setattr("utils.auth_utils._attempt_authentication_and_set_g", _auth_ok)

    # Avoid LLM/network by stubbing generation helpers
    monkeypatch.setattr("utils.generate_sourcefiles.choose_language_level", lambda code: "B1")
    monkeypatch.setattr("utils.generate_sourcefiles.generate_topic", lambda **kwargs: "Test Topic")
    monkeypatch.setattr(
        "utils.generate_sourcefiles.generate_content",
        lambda target_language_code, title, language_level, text_type=None: ("Γειά σου κόσμε.", ["ai", "test"])  # type: ignore
    )

    url = build_url_with_query(
        client,
        generate_sourcefile_api,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )

    body = {
        "title": "Test Topic",
        "language_level": "B1",
        "sourcedir_path": "AI-generated examples",
    }

    resp = client.post(url, json=body)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["sourcedir_slug"]
    assert data["sourcefile_slug"]
    assert data["url_text_tab"].endswith(f"/language/{TEST_TARGET_LANGUAGE_CODE}/source/{data['sourcedir_slug']}/{data['sourcefile_slug']}/text")

    # Verify DB entries exist
    sd = Sourcedir.get(Sourcedir.slug == data["sourcedir_slug"])  # type: ignore
    sf = Sourcefile.get(Sourcefile.slug == data["sourcefile_slug"])  # type: ignore
    assert sd.target_language_code == TEST_TARGET_LANGUAGE_CODE
    assert sf.sourcedir == sd
    assert sf.text_target and len(sf.text_target) > 0


def test_generate_validates_level(monkeypatch, client):
    monkeypatch.setattr("utils.auth_utils._attempt_authentication_and_set_g", _auth_ok)

    url = build_url_with_query(
        client,
        generate_sourcefile_api,
        target_language_code=TEST_TARGET_LANGUAGE_CODE,
    )

    resp = client.post(url, json={"language_level": "Z0"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


