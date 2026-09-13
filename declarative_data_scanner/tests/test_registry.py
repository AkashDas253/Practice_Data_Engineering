import pytest

from registry import Registry


class TestComponent:
    stage = "test"
    type = "example"


class TestValidator:
    pass


def test_register_and_resolve_component():
    registry = Registry()

    registry.register(TestComponent)

    assert registry.resolve("test", "example") is TestComponent


def test_unknown_component_fails():
    registry = Registry()

    with pytest.raises(ValueError, match="Unknown component"):
        registry.resolve("test", "missing")


def test_register_and_resolve_validator():
    registry = Registry()

    registry.register_validator("test", TestValidator)

    assert (
        registry.resolve_validator("test")
        is TestValidator
    )


def test_unknown_validator_fails():
    registry = Registry()

    with pytest.raises(ValueError, match="Unknown validator"):
        registry.resolve_validator("missing")
