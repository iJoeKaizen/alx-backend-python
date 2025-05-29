#!/usr/bin/env python3
"""
Unit test module for utils.access_nested_map function.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map

class TestAccessNestedMap(unittest.TestCase):
    """
    Test class for the access_nested_map function.
    
    This class contains test cases to verify the correct behavior of the access_nested_map function
    when accessing values in nested dictionaries using specified paths.
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """
        Test that access_nested_map returns the correct value for given inputs.
        
        Args:
            nested_map (dict): The nested dictionary to access.
            path (tuple): The path of keys to traverse in the nested dictionary.
            expected: The expected value after traversing the path.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)
