#!/usr/bin/env python3
# tests/test_client.py
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient
from utils import get_json


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



class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""
    
    @patch('client.GithubOrgClient.org', new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org):
        """Test that _public_repos_url returns correct value from org payload"""
        # Setup test payload with known repos_url
        test_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }
        mock_org.return_value = test_payload
        
        # Create client instance
        client = GithubOrgClient("google")
        
        # Access the property (no parentheses needed)
        result = client._public_repos_url
        
        # Verify result matches expected value
        self.assertEqual(result, test_payload["repos_url"])
        
        # Verify the org property was accessed
        mock_org.assert_called_once()

if __name__ == "__main__":
    unittest.main()
