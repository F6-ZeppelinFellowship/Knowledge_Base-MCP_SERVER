"""
Tests for the document upload endpoint, specifically verifying that the
label-resolution fix works correctly so uploads never fail with
"Ingestion failed: label empty or too long".

Uses FastAPI dependency_overrides to inject an in-memory Qdrant instance
so no running Qdrant server is required.
"""

import io
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.documents import get_storage
from app.db.qdrant import QdrantStorage

from app.api.documents import get_current_user

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def override_storage():
    """
    Replace the production Qdrant singleton with an isolated in-memory
    instance for every test in this module.
    """
    mem_storage = QdrantStorage(location=":memory:")

    # Override storage dependency
    app.dependency_overrides[get_storage] = lambda: mem_storage
    
    # Override auth dependency to return a mock user
    app.dependency_overrides[get_current_user] = lambda: "test_user@example.com"
    
    yield
    
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


# Minimal valid plain-text content (works for .txt and .md)
_TEXT_CONTENT = b"This is a test document about Python programming and software engineering."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _upload(client, label=None, filename="test.txt", content=_TEXT_CONTENT, user_id="test_user"):
    """POST to /documents/upload and return the response."""
    data = {"user_id": user_id}
    if label is not None:
        data["label"] = label
    return client.post(
        "/documents/upload",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
        data=data,
    )


# ---------------------------------------------------------------------------
# Label resolution tests (THE FIX)
# ---------------------------------------------------------------------------

def test_upload_without_label_uses_filename_stem(client):
    """
    BUG REPRO: uploading without a `label` field previously caused
    'Ingestion failed: label empty or too long'.
    It should now succeed and use the filename stem as the label.
    """
    resp = _upload(client, label=None, filename="my_notes.txt")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["label"] == "my_notes"   # stem of "my_notes.txt"
    assert body["status"] == "uploaded"


def test_upload_with_explicit_label(client):
    """An explicit label must be respected."""
    resp = _upload(client, label="Week 3 Report", filename="report.txt")
    assert resp.status_code == 201, resp.text
    assert resp.json()["label"] == "Week 3 Report"


def test_upload_with_blank_label_falls_back_to_filename(client):
    """Sending label='' (empty string) should fall back to the filename stem."""
    resp = _upload(client, label="", filename="lecture_notes.txt")
    assert resp.status_code == 201, resp.text
    assert resp.json()["label"] == "lecture_notes"


def test_upload_with_whitespace_only_label_falls_back(client):
    """Sending label='   ' (whitespace-only) should fall back to the filename stem."""
    resp = _upload(client, label="   ", filename="slides.txt")
    assert resp.status_code == 201, resp.text
    assert resp.json()["label"] == "slides"


def test_upload_with_long_label_is_truncated_not_rejected(client):
    """
    A label exceeding 255 chars should be silently truncated rather than
    causing a 500 error.
    """
    long_label = "A" * 400
    resp = _upload(client, label=long_label, filename="doc.txt")
    assert resp.status_code == 201, resp.text
    assert len(resp.json()["label"]) == 255


def test_upload_filename_with_spaces_and_no_label(client):
    """
    Reproduces the exact scenario from the screenshot:
    filename = 'AI Study Companion - Week 3 Report.txt', no label supplied.
    (Using .txt so we don't need a real PDF binary for this label test.)
    """
    resp = _upload(
        client,
        label=None,
        filename="AI Study Companion - Week 3 Report.txt",
        content=_TEXT_CONTENT,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["label"] == "AI Study Companion - Week 3 Report"
    assert body["status"] == "uploaded"


def test_upload_empty_file_returns_422(client):
    """Uploading a zero-byte file should return 422."""
    resp = _upload(client, content=b"", filename="empty.txt")
    assert resp.status_code == 422


def test_health_endpoint(client):
    """Sanity check that the health endpoint is reachable."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
