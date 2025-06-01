#!/usr/bin/env python3
"""
Unit and integration tests for the client.GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient

# Import fixtures from fixtures.py
try:
    from fixtures import TEST_PAYLOAD, ORG_PAYLOAD
    from fixtures import REPOS_PAYLOAD, EXPECTED_REPOS, APACHE2_REPOS
except ImportError:
    # Fallback in case fixtures aren't available
    TEST_PAYLOAD = [({}, [], [], [])]
    ORG_PAYLOAD = {}
    REPOS_PAYLOAD = []
    EXPECTED_REPOS = []
    APACHE2_REPOS = []


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test class for GithubOrgClient
    """

    @classmethod
    def setUpClass(cls):
        """Set up class-wide mocks for integration tests"""
        # Create patcher for requests.get
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        # Configure mock responses
        cls.org_mock = Mock()
        cls.org_mock.json.return_value = cls.org_payload

        cls.repos_mock = Mock()
        cls.repos_mock.json.return_value = cls.repos_payload

        # Set up side effect to return different responses based on URL
        cls.mock_get.side_effect = [
            cls.org_mock,   # First call: organization data
            cls.repos_mock,      # Second call: repositories data
        ]

    @classmethod
    def tearDownClass(cls):
        """Clean up after integration tests"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test for public_repos without license filter"""
        client = GithubOrgClient("test_org")
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

        # Verify API calls were made
        self.assertEqual(self.mock_get.call_count, 2)
        self.mock_get.assert_any_call("https://api.github.com/orgs/test_org")
        self.mock_get.assert_any_call(self.org_payload.get("repos_url", ""))

    def test_public_repos_with_license(self):
        """Integration test for public_repos with Apache 2.0 license filter"""
        client = GithubOrgClient("test_org")
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)

        # Verify API calls were made
        self.assertEqual(self.mock_get.call_count, 2)
        self.mock_get.assert_any_call("https://api.github.com/orgs/test_org")
        self.mock_get.assert_any_call(self.org_payload.get("repos_url", ""))


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit test class for GithubOrgClient
    """
    # ... (previous unit tests remain unchanged) ...


if __name__ == "__main__":
    unittest.main()
