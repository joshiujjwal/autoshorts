"""Smoke test — validates the test runner and basic imports work."""


def test_smoke() -> None:
    assert True


def test_src_importable() -> None:
    """Verify the package structure is importable."""
    import importlib

    # These should not raise ImportError once pyproject.toml is installed
    # For now just verify the test framework itself works
    assert importlib.util.find_spec("pytest") is not None
