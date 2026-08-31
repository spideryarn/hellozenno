"""Tests for the audio-variant plumbing shared by the lemma and sentence APIs.

These pin down two failures that both looked like success from the outside:
a persistence error reported as HTTP 200 with no audio, and a variants list
that the client had to re-read from a publicly-cached endpoint.
"""

import pytest

from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime

import psycopg2
from peewee import __exception_wrapper__

from db_models import Lemma, LemmaAudio
from utils.audio_utils import _is_duplicate_variant_error
from views.lemma_api import _serialise_lemma_audio_variants
from views.sentence_api import _serialise_sentence_audio_variants


class _PgError(psycopg2.IntegrityError):
    """A psycopg2 error carrying a SQLSTATE, whose pgcode is read-only."""

    def __init__(self, message: str, pgcode: str):
        super().__init__(message)
        self._pgcode = pgcode

    @property
    def pgcode(self) -> str:
        return self._pgcode


def _wrapped_pg_error(pgcode: str) -> Exception:
    """Raise a driver error through peewee's real wrapper and return the result.

    Deliberately not hand-built: peewee 3.18 re-raises inside a context manager,
    so the driver error lands in __context__ rather than __cause__. A fabricated
    chain hid that, and the classifier read only __cause__ - the test passed
    while production could not recognise a real uniqueness violation.
    """
    try:
        with __exception_wrapper__:
            raise _PgError(f"driver error {pgcode}", pgcode)
    except Exception as exc:
        return exc
    raise AssertionError("expected the wrapper to re-raise")


def _fake_variant(variant_id: int = 7):
    return SimpleNamespace(
        id=variant_id,
        provider="elevenlabs",
        metadata={"voice_name": "Alice"},
        created_at=datetime(2026, 1, 2, 3, 4, 5),
    )


class TestIsDuplicateVariantError:
    """Only a real uniqueness collision may be swallowed as 'already there'."""

    def test_wrapped_unique_violation_is_a_duplicate(self):
        assert _is_duplicate_variant_error(_wrapped_pg_error("23505"))

    def test_unique_violation_on_the_exception_itself_is_a_duplicate(self):
        assert _is_duplicate_variant_error(_PgError("duplicate key", "23505"))

    def test_foreign_key_violation_is_not_a_duplicate(self):
        # 23503 is foreign_key_violation - a created_by pointing at a missing
        # user. Peewee maps this to IntegrityError just like a unique violation,
        # so classifying by exception type is what turned a genuine persistence
        # failure into a 200 with an empty variants list.
        assert not _is_duplicate_variant_error(_wrapped_pg_error("23503"))

    def test_not_null_violation_is_not_a_duplicate(self):
        assert not _is_duplicate_variant_error(_wrapped_pg_error("23502"))

    def test_arbitrary_error_is_not_a_duplicate(self):
        assert not _is_duplicate_variant_error(RuntimeError("connection lost"))


class TestSerialiseVariants:
    def test_lemma_variant_url_targets_the_specific_variant(self):
        [out] = _serialise_lemma_audio_variants("el", "καλός", [_fake_variant()])
        assert out["id"] == 7
        assert out["provider"] == "elevenlabs"
        assert out["metadata"] == {"voice_name": "Alice"}
        # The lemma must be percent-encoded, and the id pinned, so playback
        # doesn't re-randomise the voice on every fetch.
        assert out["url"] == (
            "/api/lang/lemma/el/%CE%BA%CE%B1%CE%BB%CF%8C%CF%82/audio?variant_id=7"
        )

    def test_sentence_variant_url_targets_the_specific_variant(self):
        [out] = _serialise_sentence_audio_variants("el", 42, [_fake_variant()])
        assert out["url"] == "/api/lang/sentence/el/42/audio?variant_id=7"

    def test_missing_metadata_becomes_an_empty_dict(self):
        variant = _fake_variant()
        variant.metadata = None
        [out] = _serialise_lemma_audio_variants("el", "x", [variant])
        assert out["metadata"] == {}


@pytest.fixture
def bind_audio_utils_db(fixture_for_testing_db):
    """Point audio_utils at the test database.

    audio_utils does `from utils.db_connection import database` at import time,
    which captures None because init_db only assigns the module global later.
    """
    import utils.audio_utils as audio_utils

    with patch.object(audio_utils, "database", fixture_for_testing_db):
        yield


class TestEnsureLemmaAudioApi:
    """The ensure endpoint must never report success when nothing was stored.

    This is the regression the whole change exists for: a failed insert used to
    be swallowed at DEBUG level, so the endpoint answered 200 with an empty
    variants list and the UI said "No audio available." for audio it had just
    paid to generate.
    """

    def _lemma(self):
        return Lemma.create(
            lemma="δοκιμή",
            target_language_code="el",
            translations=["test"],
            part_of_speech="noun",
            is_complete=True,
        )

    def test_returns_the_variants_it_created(self, client, bind_audio_utils_db):
        lemma = self._lemma()
        resp = client.post(f"/api/lang/lemma/el/{lemma.lemma}/audio/ensure?n=2")

        assert resp.status_code == 200
        body = resp.get_json()
        # The client plays straight from this list rather than re-reading the
        # publicly-cached listing endpoint, so it must actually be present.
        assert body["created"] == 2
        assert len(body["variants"]) == 2
        for variant in body["variants"]:
            assert variant["url"].endswith(f"variant_id={variant['id']}")
            assert variant["metadata"]["voice_name"]

    def test_persistence_failure_is_a_500_not_a_false_success(
        self, client, bind_audio_utils_db
    ):
        lemma = self._lemma()
        boom = _wrapped_pg_error("23503")  # foreign_key_violation, not a duplicate

        with patch.object(LemmaAudio, "create", side_effect=boom):
            resp = client.post(f"/api/lang/lemma/el/{lemma.lemma}/audio/ensure?n=1")

        assert resp.status_code == 500
        body = resp.get_json()
        assert "created" not in body
        # And the raw driver text must not leak to the client.
        assert "23503" not in str(body)
        assert "driver error" not in str(body)

    def test_a_duplicate_insert_is_still_tolerated(self, client, bind_audio_utils_db):
        lemma = self._lemma()
        dupe = _wrapped_pg_error("23505")  # another request won the race

        with patch.object(LemmaAudio, "create", side_effect=dupe):
            resp = client.post(f"/api/lang/lemma/el/{lemma.lemma}/audio/ensure?n=1")

        assert resp.status_code == 200
        assert resp.get_json()["created"] == 0
