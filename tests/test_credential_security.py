from __future__ import annotations

import pytest

from causal_mind.security.credentials import assert_no_secrets, scan_for_secrets


def test_clean_text_passes() -> None:
    assert scan_for_secrets("just a normal research sentence\nwith numbers 12345") == []


def test_detects_jwt() -> None:
    head = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9"
    payload = "eyJzdWIiOiIxMjM0NTY3ODkwIn0"
    sig = "dozjgNryP4J3jVmNHl0w5N_Xgt0K3Sttl9bZJYe3J6o"
    text = f"token: {head}.{payload}.{sig}"
    findings = scan_for_secrets(text)
    assert any(f.kind == "jwt" for f in findings)


def test_detects_private_key() -> None:
    text = "-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----"
    findings = scan_for_secrets(text)
    assert any(f.kind == "private-key-block" for f in findings)


def test_detects_aws_key() -> None:
    text = "aws: AKIAIOSFODNN7EXAMPLE"
    findings = scan_for_secrets(text)
    assert any(f.kind == "aws-access-key" for f in findings)


def test_assert_raises() -> None:
    with pytest.raises(ValueError):
        assert_no_secrets("key AKIAIOSFODNN7EXAMPLE here")


def test_generic_api_key() -> None:
    text = 'api_key = "abcdef1234567890abcdef1234567890"'
    findings = scan_for_secrets(text)
    assert any(f.kind == "generic-api-key" for f in findings)
