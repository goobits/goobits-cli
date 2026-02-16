"""Unit tests for core utility helpers."""

from goobits_cli.core.utils import safe_get_attr, safe_to_dict


class _ModelDump:
    def model_dump(self):
        return {"a": 1}


class _ModelDumpFail:
    def model_dump(self):
        raise RuntimeError("fail")

    def dict(self):
        return {"b": 2}


class _DictFail:
    def dict(self):
        raise RuntimeError("fail")

    def __init__(self):
        self.c = 3


def test_safe_to_dict_handles_none_and_dict_passthrough():
    assert safe_to_dict(None) == {}
    data = {"x": 1}
    assert safe_to_dict(data) is data


def test_safe_to_dict_prefers_model_dump_then_dict_then_vars():
    assert safe_to_dict(_ModelDump()) == {"a": 1}
    assert safe_to_dict(_ModelDumpFail()) == {"b": 2}

    as_vars = safe_to_dict(_DictFail())
    assert as_vars.get("c") == 3


def test_safe_to_dict_returns_empty_when_unconvertible():
    class _NoAttrs:
        __slots__ = ()

    assert safe_to_dict(_NoAttrs()) == {}


def test_safe_get_attr_supports_dict_object_and_defaults():
    assert safe_get_attr({"k": 7}, "k", 0) == 7
    assert safe_get_attr({"k": 7}, "missing", 9) == 9

    class Obj:
        value = 42

    assert safe_get_attr(Obj(), "value", 0) == 42
    assert safe_get_attr(Obj(), "missing", 5) == 5
    assert safe_get_attr(None, "anything", "d") == "d"

