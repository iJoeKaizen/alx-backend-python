#!/usr/bin/env python3
"""
Unit tests for utility functions in utils module.
Covers: access_nested_map, get_json, memoize.
"""

import pytest
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize

class TestAccessNestedMap:
    @pytest.mark.parametrize("nested_map, path, expected", [
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
        ({"a": {"b": {"c": 3}}}, ("a", "b", "c"), 3),
        ({"x": {"y": {"z": [1, 2, 3]}}}, ("x", "y", "z", 1), 2),
        ({"a": 1}, (), {"a": 1}),  # Empty path
    ])
    def test_access_nested_map_valid(self, nested_map, path, expected):
        assert access_nested_map(nested_map, path) == expected

    @pytest.mark.parametrize("nested_map, path, missing_key", [
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
        ({"a": {"b": 2}}, ("a", "x"), "x"),
        ({"a": {}}, ("a", "b"), "b"),
        ({"x": {"y": {"z": None}}}, ("x", "y", "z", "a"), "a"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, missing_key):
        with pytest.raises(KeyError) as exc_info:
            access_nested_map(nested_map, path)
        assert str(exc_info.value) == f"'{missing_key}'"


class TestGetJson:
    @pytest.mark.parametrize("url, payload", [
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
        ("https://api.github.com", {"data": "test"}),
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
            with pytest.raises(ValueError, match="Invalid JSON"):
                get_json("http://example.com")


class TestMemoize:
    def test_memoize_caches_result(self):
        class TestClass:
            def a_method(self):
                return 42
            
            @memoize
            def a_property(self):
                return self.a_method()
        
        with patch.object(TestClass, "a_method", return_value=42) as mock_method:
            test = TestClass()
            assert test.a_property() == 42
            assert test.a_property() == 42
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
        
        with patch.object(TestClass, "compute") as mock_compute:
            # Return different values for different instances
            mock_compute.side_effect = [99, 100]
            t1 = TestClass(1)
            t2 = TestClass(2)
            
            # First calls (compute should be called)
            assert t1.cached_value() == 99
            assert t2.cached_value() == 100
            
            # Second calls (should use cache)
            assert t1.cached_value() == 99
            assert t2.cached_value() == 100
            
            # Verify compute was called only once per instance
            assert mock_compute.call_count == 2

    def test_memoize_cache_isolation_between_methods(self):
        class TestClass:
            @memoize
            def method1(self):
                return 1
            
            @memoize
            def method2(self):
                return 2
        
        with patch.multiple(TestClass,
                            method1=Mock(return_value=1),
                            method2=Mock(return_value=2)) as mocks:
            test = TestClass()
            assert test.method1() == 1
            assert test.method2() == 2
            assert test.method1() == 1
            assert test.method2() == 2
            
            mocks["method1"].assert_called_once()
            mocks["method2"].assert_called_once()
