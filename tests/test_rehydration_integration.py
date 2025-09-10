import importlib.util
from pathlib import Path


def _load_module_by_path():
    mod_path = Path("scripts/rehydration_integration.py").resolve()
    spec = importlib.util.spec_from_file_location("rehydration_integration", str(mod_path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def test_disabled_flag_returns_false(tmp_path, monkeypatch):
    mod = _load_module_by_path()
    # Redirect state file to a temp path
    mod.STATE_PATH = Path(tmp_path / ".rehydrate_state.json")

    monkeypatch.setenv("AUTO_REHYDRATE", "0")
    monkeypatch.setenv("REHYDRATE_MINUTES", "10")

    assert mod.is_enabled() is False
    assert mod.should_trigger("B-TEST") is False


def test_debounce_logic(tmp_path, monkeypatch):
    mod = _load_module_by_path()
    # Redirect state file to a temp path
    mod.STATE_PATH = Path(tmp_path / ".rehydrate_state.json")

    monkeypatch.setenv("AUTO_REHYDRATE", "1")
    monkeypatch.setenv("REHYDRATE_MINUTES", "10")

    backlog_id = "B-TEST"

    # First attempt should be allowed
    assert mod.should_trigger(backlog_id) is True
    mod.record_trigger(backlog_id)

    # Immediate subsequent attempt should be blocked by debounce
    assert mod.should_trigger(backlog_id) is False

    # If debounce window is set to 0, should allow immediately
    monkeypatch.setenv("REHYDRATE_MINUTES", "0")
    assert mod.should_trigger(backlog_id) is True
