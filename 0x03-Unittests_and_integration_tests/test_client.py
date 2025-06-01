# tests/test_integration_client.py

#!/usr/bin/env python3
"""
Integration tests for GithubOrgClient.public_repos using fixtures.
"""
import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized_class
from client import GithubOrgClient
import fixtures


@parameterized_class([{
    "org_payload": fixtures.org_payload,
    "repos_payload": fixtures.repos_payload,
    "expected_repos": fixtures.expected_repos,
    "apache2_repos": fixtures.apache2_repos,
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Start patching requests.get with fixture-based side_effect"""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            response = MagicMock()
            if url == "https://api.github.com/orgs/google":
                response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                response.json.return_value = cls.repos_payload
            return response

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop requests.get patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns all expected repo names"""
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos returns only repos with apache-2.0 license"""
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)
