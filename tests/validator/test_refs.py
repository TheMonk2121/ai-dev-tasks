import subprocess

from scripts.doc_coherence_validator import check_markdown_references


def _sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


def test_reference_checking(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    _sh(["git", "init", "-b", "main"], repo)

    docs = repo / "docs"
    docs.mkdir()
    (docs / "live.md").write_text("# live\n", encoding="utf-8")
    (docs / "moved.md").write_text("# moved\n", encoding="utf-8")

    # Commit baseline
    _sh(["git", "add", "."], repo)
    _sh(["git", "commit", "-m", "init"], repo)

    # Rename moved.md -> archived/moved.md
    archived = docs / "archived"
    archived.mkdir()
    _sh(["git", "mv", str(docs / "moved.md"), str(archived / "moved.md")], repo)
    _sh(["git", "commit", "-m", "rename moved"], repo)

    # Create source doc with variety of refs
    src = docs / "source.md"
    src.write_text(
        "\n".join(
            [
                "# Source",
                "OK link: [Live](live.md)",
                "Fragment link: [Sec](archived/moved.md#section-1)",
                "Broken link: [Missing](missing.md)",
                "Backtick existing: `live.md`",
                "Backtick missing: `ghost.md`",
                "```",
                "example with `ignored.md` inside code fence",
                "```",
            ]
        ),
        encoding="utf-8",
    )

    text = src.read_text(encoding="utf-8")
    errs, warns, _ = check_markdown_references(src, text, enforce_lowercase=True)

    # Assertions: 1 broken link error, no errors for OK/fragment
    assert any("Link target not found: missing.md" in e for e in errs)
    assert not any("live.md" in e for e in errs)
    assert not any("archived/moved.md" in e for e in errs)

    # Style warnings for backticks (+ one for missing backtick)
    assert any("Use Markdown link instead of backtick for: live.md" in w for w in warns)
    assert any("Backticked file reference not found: ghost.md" in w for w in warns)

    # Code fence reference is ignored
    assert not any("ignored.md" in w for w in warns)
