"""
Tests for the ESI client module.
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock
from rataura.esi.client import ESIClient


class TestESIClient(unittest.TestCase):
    """
    Test case for the ESI client.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        self.client = ESIClient()
    
    @patch('aiohttp.ClientSession.get')
    def test_get(self, mock_get):
        """
        Test the get method.
        """
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {"test": "data"})
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Call the method
        result = asyncio.run(self.client.get("/test/"))
        
        # Check the result
        self.assertEqual(result, {"test": "data"})
        mock_get.assert_called_once()
    
    @patch('aiohttp.ClientSession.post')
    def test_post(self, mock_post):
        """
        Test the post method.
        """
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {"test": "data"})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Call the method
        result = asyncio.run(self.client.post("/test/", {"data": "test"}))
        
        # Check the result
        self.assertEqual(result, {"test": "data"})
        mock_post.assert_called_once()
    
    @patch('rataura.esi.client.ESIClient.get')
    def test_get_alliances(self, mock_get):
        """
        Test the get_alliances method.
        """
        # Set up the mock
        mock_get.return_value = asyncio.Future()
        mock_get.return_value.set_result([1, 2, 3])
        
        # Call the method
        result = asyncio.run(self.client.get_alliances())
        
        # Check the result
        self.assertEqual(result, [1, 2, 3])
        mock_get.assert_called_once_with("/alliances/")
    
    @patch('rataura.esi.client.ESIClient.get')
    def test_get_alliance(self, mock_get):
        """
        Test the get_alliance method.
        """
        # Set up the mock
        mock_get.return_value = asyncio.Future()
        mock_get.return_value.set_result({"name": "Test Alliance"})
        
        # Call the method
        result = asyncio.run(self.client.get_alliance(123))
        
        # Check the result
        self.assertEqual(result, {"name": "Test Alliance"})
        mock_get.assert_called_once_with("/alliances/123/")


if __name__ == "__main__":
    unittest.main()
