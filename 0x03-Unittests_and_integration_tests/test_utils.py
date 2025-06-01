#!/usr/bin/env python3
# tests/test_memoize.py
import unittest
from unittest.mock import patch
from utils import memoize


class TestMemoize(unittest.TestCase):
    """
    Unit test for utils.memoize decorator
    """

    def test_memoize(self):
        """
        Test that a_property is cached and a_method is only called once
        """
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method', return_value=42) as mock_method:
            test_instance = TestClass()
            self.assertEqual(test_instance.a_property(), 42)
            self.assertEqual(test_instance.a_property(), 42)
            mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
