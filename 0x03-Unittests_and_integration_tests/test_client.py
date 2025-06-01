#!/usr/bin/env python3
"""
Unit tests for the client.GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient

# Import fixtures from fixtures.py
try:
    from fixtures import (TEST_PAYLOAD, ORG_PAYLOAD, REPOS_PAYLOAD,
                          EXPECTED_REPOS, APACHE2_REPOS)
except ImportError:
    # Fallback in case fixtures aren't available
    TEST_PAYLOAD = [({}, [], [], [])]
    ORG_PAYLOAD = {}
    REPOS_PAYLOAD = []
    EXPECTED_REPOS = []
    APACHE2_REPOS = []


@parameterized_class(("org_payload", "repos_payload", "expected_repos", "apache2_repos"), TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test class for GithubOrgClient
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up class-wide mocks"""
        # Create patcher for requests.get
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        
        # Configure mock response for organization
        org_mock = Mock()
        org_mock.json.return_value = cls.org_payload
        
        # Configure mock response for repositories
        repos_mock = Mock()
        repos_mock.json.return_value = cls.repos_payload
        
        # Set up side effect to return different responses based on URL
        cls.mock_get.side_effect = [
            org_mock,       # First call: organization data
            repos_mock,     # Second call: repositories data
        ]

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos without license filter"""
        client = GithubOrgClient("test_org")
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter"""
        client = GithubOrgClient("test_org")
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit test class for GithubOrgClient
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """
        Test that GithubOrgClient.org returns expected result
        and get_json is called once with the right URL.
        """
        expected_payload = {"login": org_name, "id": 12345}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self):
        """Test that _public_repos_url returns correct value from org payload"""
        test_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
        
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("google")
            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])
            mock_org.assert_called_once()
            
    def test_public_repos(self):
        """Test that public_repos returns correct list of repositories"""
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        
        with patch('client.get_json', return_value=repos_payload) as mock_get:
            with patch('client.GithubOrgClient._public_repos_url',
                       new_callable=PropertyMock) as mock_pub_url:
                mock_pub_url.return_value = "https://example.com/repos"
                client = GithubOrgClient("google")
                repos = client.public_repos()
                expected_repos = ["repo1", "repo2", "repo3"]
                self.assertEqual(repos, expected_repos)
                mock_pub_url.assert_called_once()
                mock_get.assert_called_once_with("https://example.com/repos")
                
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """Test that has_license correctly identifies license presence"""
        client = GithubOrgClient("test_org")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
