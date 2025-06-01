#!/usr/bin/env python3
"""
Unit tests for the client.GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


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
