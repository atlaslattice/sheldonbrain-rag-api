"""Governance-contract tests for Sheldonbrain RAG API.

These tests intentionally avoid live Gemini or Pinecone calls. They protect the
product invariants that make Sheldonbrain more than a vector database wrapper.
"""
import re

import rag_api_gemini as api


def test_content_hash_is_stable_sha256_receipt():
    first = api.content_hash("memory != permission")
    second = api.content_hash("memory != permission")

    assert first == second
    assert re.fullmatch(r"sha256:[a-f0-9]{64}", first)


def test_governance_defaults_preserve_lifecycle_and_authority_boundary():
    metadata = {"source": "gpt", "model": "gpt-5.5-thinking"}

    governed = api.apply_governance_defaults("Nothing dies.", metadata)

    assert governed["lifecycle"] == "active"
    assert governed["ratification"] == "unratified"
    assert governed["execution_authority"] is False
    assert governed["created_by_agent"] == "gpt"
    assert governed["created_by_model"] == "gpt-5.5-thinking"
    assert governed["source_type"] == "api"
    assert governed["content_hash"].startswith("sha256:")


def test_governance_defaults_do_not_overwrite_explicit_metadata():
    metadata = {
        "lifecycle": "quarantined",
        "ratification": "reviewed",
        "execution_authority": False,
        "created_by_agent": "lucerna",
        "created_by_model": "manual-review",
        "source_type": "repo",
        "source_uri": "https://example.invalid/artifact",
    }

    governed = api.apply_governance_defaults("Receipt beats vibes.", metadata)

    assert governed["lifecycle"] == "quarantined"
    assert governed["ratification"] == "reviewed"
    assert governed["created_by_agent"] == "lucerna"
    assert governed["created_by_model"] == "manual-review"
    assert governed["source_type"] == "repo"
    assert governed["source_uri"] == "https://example.invalid/artifact"


def test_lifecycle_visibility_hides_archival_states_by_default():
    assert api.lifecycle_is_visible({"lifecycle": "active"}) is True
    assert api.lifecycle_is_visible({"lifecycle": "superseded"}) is True
    assert api.lifecycle_is_visible({"lifecycle": "archived"}) is False
    assert api.lifecycle_is_visible({"lifecycle": "quarantined"}) is False
    assert api.lifecycle_is_visible({"lifecycle": "redacted_pointer"}) is False


def test_lifecycle_visibility_can_include_archived_records_when_requested():
    assert api.lifecycle_is_visible(
        {"lifecycle": "archived"},
        include_archived=True,
    ) is True


def test_lifecycle_operations_are_non_destructive_product_states():
    assert api.LIFECYCLE_OPERATIONS == {
        "archive": "archived",
        "quarantine": "quarantined",
        "supersede": "superseded",
        "redact_pointer": "redacted_pointer",
        "restore": "active",
    }


def test_retrieval_receipt_contains_audit_fields(monkeypatch):
    class FakeRag:
        namespace = "baseline"

    monkeypatch.setattr(api, "rag", FakeRag())

    receipt = api.build_retrieval_receipt(
        query_text="What changed?",
        top_k=5,
        filter_dict={"sphere": {"$eq": "H02.S11"}},
        include_archived=False,
        elapsed_ms=12.345,
    )

    assert receipt["query_hash"].startswith("sha256:")
    assert receipt["index"] == api.PINECONE_INDEX
    assert receipt["namespace"] == "baseline"
    assert receipt["filters"] == {"sphere": {"$eq": "H02.S11"}}
    assert receipt["top_k"] == 5
    assert receipt["include_archived"] is False
    assert receipt["ontology_version"] == api.ONTOLOGY_VERSION
    assert receipt["query_time_ms"] == 12.35
