#!/usr/bin/env python3
"""
Unit tests for utility functions in utils module.
Covers: access_nested_map, get_json, memoize.
"""

# tests/test_utils.py
import pytest
import unittest
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize

class TestAccessNestedMap:
    @pytest.mark.parametrize("nested_map, path, expected", [
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
        ({"a": {"b": {"c": 3}}}, ("a", "b", "c"), 3),
    ])
    def test_access_nested_map_valid(self, nested_map, path, expected):
        assert access_nested_map(nested_map, path) == expected

    @pytest.mark.parametrize("nested_map, path, missing_key", [
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
        ({"a": {"b": 2}}, ("a", "x"), "x"),
        ({"a": {}}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, missing_key):
        with pytest.raises(KeyError) as exc_info:
            access_nested_map(nested_map, path)
        assert str(exc_info.value) == f"'{missing_key}'"


class TestGetJson:
    @pytest.mark.parametrize("url, payload", [
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json_success(self, url, payload):
        with patch("utils.requests.get") as mock_get:
            mock_resp = Mock()
            mock_resp.json.return_value = payload
            mock_get.return_value = mock_resp
            result = get_json(url)
            mock_get.assert_called_once_with(url)
            assert result == payload

    def test_get_json_invalid_json(self):
        with patch("utils.requests.get") as mock_get:
            mock_resp = Mock()
            mock_resp.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_resp
            with pytest.raises(ValueError):
                get_json("http://example.com")


class TestMemoize(unittest.TestCase):
    def test_memoize(self):
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, "a_method", return_value=42) as mock_method:
            test = TestClass()
            self.assertEqual(test.a_property(), 42)
            self.assertEqual(test.a_property(), 42)
            mock_method.assert_called_once()

    def test_memoize_multiple_instances(self):
        class TestClass:
            def __init__(self, value):
                self._value = value

            def compute(self):
                return self._value

            @memoize
            def cached_value(self):
                return self.compute()

        with patch.object(TestClass, "compute", return_value=99) as mock_method:
            t1 = TestClass(1)
            t2 = TestClass(2)
            self.assertEqual(t1.cached_value(), 99)
            self.assertEqual(t2.cached_value(), 99)
            self.assertEqual(t1.cached_value(), 99)
            self.assertEqual(t2.cached_value(), 99)
            self.assertEqual(mock_method.call_count, 2)
