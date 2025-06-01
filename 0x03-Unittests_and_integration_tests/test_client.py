#!/usr/bin/env python3
# tests/test_client.py
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
        # Setup test payload with known repos_url
        test_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }
        
        # Patch the org property using context manager
        with patch('client.GithubOrgClient.org', 
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            
            # Create client instance
            client = GithubOrgClient("google")
            
            # Access the property
            result = client._public_repos_url
            
            # Verify result matches expected value
            self.assertEqual(result, test_payload["repos_url"])
            
            # Verify the org property was accessed
            mock_org.assert_called_once()
            
    def test_public_repos(self):
        """Test that public_repos returns the correct list of repositories"""
        # Define test payload for repositories
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        
        # Mock get_json to return our test payload
        with patch('client.get_json', return_value=repos_payload) as mock_get_json:
            # Mock _public_repos_url property to return a known URL
            with patch('client.GithubOrgClient._public_repos_url',
                       new_callable=PropertyMock) as mock_public_repos_url:
                mock_public_repos_url.return_value = "https://api.github.com/orgs/google/repos"
                
                # Create client instance
                client = GithubOrgClient("google")
                
                # Call the public_repos method
                repos = client.public_repos()
                
                # Verify the list of repos is what we expect
                expected_repos = ["repo1", "repo2", "repo3"]
                self.assertEqual(repos, expected_repos)
                
                # Verify _public_repos_url property was accessed once
                mock_public_repos_url.assert_called_once()
                
                # Verify get_json was called once with the expected URL
                mock_get_json.assert_called_once_with("https://api.github.com/orgs/google/repos")


if __name__ == "__main__":
    unittest.main()
