from __future__ import annotations


def test_module_wrapper_importable() -> None:
    # Test that the module can be imported and has the expected interface
    import scripts.evaluation
    
    # Verify the module was imported successfully
    assert scripts.evaluation is not None

    # Check that the __main__.py file exists and can be imported
    from scripts.evaluation import __main__
    assert hasattr(__main__, 'main')
    assert callable(__main__.main)
