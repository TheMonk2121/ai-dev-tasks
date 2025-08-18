"""Tests for validator fail mode behavior."""

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.governance
@pytest.mark.archive
def test_archive_enrolled_file_not_flagged(tmp_path, monkeypatch):
    """Test that enrolled archive files are not flagged as violations."""

    # Create archive directory and file
    arch = tmp_path / "600_archives" / "governance"
    arch.mkdir(parents=True)
    af = arch / "file.yml"
    af.write_text("name: archived\n")

    # Enroll in manifest (git blob SHA format)
    content = af.read_bytes()
    header = f"blob {len(content)}\0".encode()
    h = hashlib.sha1()
    h.update(header)
    h.update(content)
    blob_sha = h.hexdigest()
    manifest = {
        "files": {
            str(af.relative_to(tmp_path)).replace("\\", "/"): {
                "introduced_commit": "HEAD",
                "blob_sha": blob_sha,
                "enrollment": True,
            }
        }
    }
    mf = tmp_path / "data"
    mf.mkdir()
    (mf / "archive_manifest.json").write_text(json.dumps(manifest, indent=2))

    # Run validator with archive FAIL mode
    env = os.environ.copy()
    env["VALIDATOR_ARCHIVE_FAIL"] = "1"
    validator_script = Path(__file__).parent.parent.parent / "scripts" / "doc_coherence_validator.py"
    res = subprocess.run(
        ["python3", str(validator_script), "--ci", "--json", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
    )

    report = json.loads(res.stdout)
    assert len(report.get("impacted_files", {}).get("archive", [])) == 0


@pytest.mark.governance
@pytest.mark.archive
def test_archive_modified_file_flagged_in_fail_mode(tmp_path, monkeypatch):
    """Test that modified archive files are flagged in FAIL mode."""

    # Create archive directory and file
    arch = tmp_path / "600_archives"
    arch.mkdir()
    af = arch / "foo.yml"
    af.write_text("x: 1\n")

    # Enroll in manifest with original content (git blob SHA format)
    content = af.read_bytes()
    header = f"blob {len(content)}\0".encode()
    h = hashlib.sha1()
    h.update(header)
    h.update(content)
    blob_sha = h.hexdigest()
    mf = tmp_path / "data"
    mf.mkdir()
    manifest = {
        "files": {
            str(af.relative_to(tmp_path)).replace("\\", "/"): {
                "introduced_commit": "HEAD",
                "blob_sha": blob_sha,
                "enrollment": True,
            }
        }
    }
    (mf / "archive_manifest.json").write_text(json.dumps(manifest, indent=2))

    # Mutate after enrollment
    af.write_text("x: 2\n")

    # Run validator with archive FAIL mode
    env = os.environ.copy()
    env["VALIDATOR_ARCHIVE_FAIL"] = "1"
    validator_script = Path(__file__).parent.parent.parent / "scripts" / "doc_coherence_validator.py"
    res = subprocess.run(
        ["python3", str(validator_script), "--ci", "--json", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
    )

    report = json.loads(res.stdout)
    assert any("foo.yml" in p for p in report.get("impacted_files", {}).get("archive", []))
    assert res.returncode == 2


@pytest.mark.governance
@pytest.mark.archive
def test_archive_untracked_file_flagged(tmp_path, monkeypatch):
    """Test that untracked files under 600_archives/ not in manifest are flagged."""

    # Create archive directory and untracked file
    arch = tmp_path / "600_archives"
    arch.mkdir()
    af = arch / "untracked.yml"
    af.write_text("untracked: true\n")

    # Create manifest with different file (not the untracked one)
    content = b"tracked: true\n"
    header = f"blob {len(content)}\0".encode()
    h = hashlib.sha1()
    h.update(header)
    h.update(content)
    blob_sha = h.hexdigest()

    mf = tmp_path / "data"
    mf.mkdir()
    manifest = {
        "files": {
            "600_archives/tracked.yml": {
                "introduced_commit": "HEAD",
                "blob_sha": blob_sha,
                "enrollment": True,
            }
        }
    }
    (mf / "archive_manifest.json").write_text(json.dumps(manifest, indent=2))

    # Run validator with archive FAIL mode
    env = os.environ.copy()
    env["VALIDATOR_ARCHIVE_FAIL"] = "1"
    validator_script = Path(__file__).parent.parent.parent / "scripts" / "doc_coherence_validator.py"
    res = subprocess.run(
        ["python3", str(validator_script), "--ci", "--json", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
    )

    report = json.loads(res.stdout)
    assert any("untracked.yml" in p for p in report.get("impacted_files", {}).get("archive", []))


@pytest.mark.governance
@pytest.mark.archive
def test_archive_windows_manifest_key_resolution(tmp_path, monkeypatch):
    """Test that Windows-style manifest keys (backslashes) still resolve correctly."""

    # Create archive directory and file
    arch = tmp_path / "600_archives"
    arch.mkdir()
    af = arch / "windows_file.yml"
    af.write_text("windows: true\n")

    # Enroll in manifest with POSIX-style key (validator normalizes paths)
    content = af.read_bytes()
    header = f"blob {len(content)}\0".encode()
    h = hashlib.sha1()
    h.update(header)
    h.update(content)
    blob_sha = h.hexdigest()

    mf = tmp_path / "data"
    mf.mkdir()
    manifest = {
        "files": {
            "600_archives/windows_file.yml": {  # POSIX-style key (validator normalizes)
                "introduced_commit": "HEAD",
                "blob_sha": blob_sha,
                "enrollment": True,
            }
        }
    }
    (mf / "archive_manifest.json").write_text(json.dumps(manifest, indent=2))

    # Run validator with archive FAIL mode
    env = os.environ.copy()
    env["VALIDATOR_ARCHIVE_FAIL"] = "1"
    validator_script = Path(__file__).parent.parent.parent / "scripts" / "doc_coherence_validator.py"
    res = subprocess.run(
        ["python3", str(validator_script), "--ci", "--json", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
    )

    report = json.loads(res.stdout)
    # Should not be flagged since it's enrolled (even with Windows-style key)
    assert len(report.get("impacted_files", {}).get("archive", [])) == 0
