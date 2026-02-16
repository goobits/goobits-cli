"""Unit tests for shared string utilities."""

import json
from types import SimpleNamespace

from goobits_cli.utils.strings import (
    escape_javascript_string,
    json_stringify,
    to_camel_case,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
)


def test_case_converters_handle_empty_and_basic_inputs():
    assert to_camel_case("") == ""
    assert to_pascal_case("") == ""
    assert to_kebab_case("") == ""
    assert to_snake_case("") == ""

    assert to_camel_case("hello_world") == "helloWorld"
    assert to_pascal_case("hello_world") == "HelloWorld"
    assert to_kebab_case("hello_world") == "hello-world"
    assert to_snake_case("hello-world") == "hello_world"


def test_case_converters_handle_mixed_formats():
    assert to_camel_case("HelloWorld") == "helloWorld"
    assert to_pascal_case("helloWorld") == "HelloWorld"
    assert to_kebab_case("HelloWorld") == "hello-world"
    assert to_snake_case("HTTPResponse") == "http_response"
    assert to_snake_case("hello World") == "hello_world"


def test_escape_javascript_string_preserves_unicode_and_escapes_control_chars():
    raw = 'Hi "there"\\path\nnew\tline\r🙂'
    escaped = escape_javascript_string(raw)

    assert '\\"' in escaped
    assert "\\\\" in escaped
    assert "\\n" in escaped
    assert "\\t" in escaped
    assert "\\r" in escaped
    assert "🙂" in escaped


def test_escape_javascript_string_non_string_falls_back_to_str():
    assert escape_javascript_string(123) == "123"
    assert escape_javascript_string(True) == "True"


class _ModelDumpObj:
    def model_dump(self):
        return {"a": 1}


class _DictObj:
    def dict(self):
        return {"b": 2}


def test_json_stringify_handles_model_dump_and_dict_and_plain_values():
    model_json = json_stringify(_ModelDumpObj())
    dict_json = json_stringify(_DictObj())
    plain_json = json_stringify({"c": 3})

    assert json.loads(model_json) == {"a": 1}
    assert json.loads(dict_json) == {"b": 2}
    assert json.loads(plain_json) == {"c": 3}

