from __future__ import annotations

import runpy


def test_module_wrapper_importable() -> None:
    # Should execute without raising; returns a dict from run_module
    mod_globals = runpy.run_module("scripts.evaluation", run_name="__main__")
    assert isinstance(mod_globals, dict)
