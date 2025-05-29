#!/usr/bin/env python3
"""
Unit test module for utils.access_nested_map function.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json
from unittest.mock import patch, Mock

class TestAccessNestedMap(unittest.TestCase):
    """
    Test class for the access_nested_map function.
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test valid path access"""
        self.assertEqual(access_nested_map(nested_map, path), expected)
        
    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b'),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test KeyError for invalid path"""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_key}'")



class TestGetJson(unittest.TestCase):
    """
    Test class for the get_json function.
    
    This class contains test cases to verify the correct behavior of the get_json function
    when fetching JSON data from URLs.
    """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """
        Test that get_json returns the expected result without making actual HTTP calls.
        
        Args:
            test_url (str): URL to fetch JSON data from.
            test_payload (dict): Expected JSON payload.
            mock_get (Mock): Mocked requests.get method.
        """
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response
        
        result = get_json(test_url)
        
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)
