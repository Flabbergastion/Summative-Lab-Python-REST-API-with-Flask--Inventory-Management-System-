"""Unit Tests for OpenFoodFacts API"""

import pytest
from unittest.mock import patch, Mock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.openfoodfacts import OpenFoodFactsAPI

@pytest.fixture
def api():
    return OpenFoodFactsAPI()

class TestOpenFoodFactsAPI:
    """OpenFoodFacts API tests"""
    
    def test_initialization(self, api):
        """Test API initialization"""
        assert api.base_url == "https://world.openfoodfacts.org/api/v2"
        assert 'User-Agent' in api.headers
    
    @patch('requests.get')
    def test_get_product_success(self, mock_get, api):
        """Test successful product retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 1,
            'product': {
                'product_name': 'Test Product',
                'brands': 'Test Brand',
                'categories_tags': ['en:beverages']
            }
        }
        mock_get.return_value = mock_response
        
        result = api.get_product_by_barcode('123456')
        assert result is not None
        assert result['product_name'] == 'Test Product'
    
    @patch('requests.get')
    def test_get_product_not_found(self, mock_get, api):
        """Test product not found"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 0}
        mock_get.return_value = mock_response
        
        result = api.get_product_by_barcode('000000')
        assert result is None
    
    @patch('requests.get')
    def test_search_products(self, mock_get, api):
        """Test product search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'products': [
                {
                    'product_name': 'Search Result',
                    'brands': 'Brand',
                    'code': '123456'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        results = api.search_products('test')
        assert len(results) == 1
        assert results[0]['product_name'] == 'Search Result'
    
    def test_format_product(self, api):
        """Test product formatting"""
        product_data = {
            'product_name': 'Test Product',
            'brands': 'Test Brand',
            'categories_tags': ['en:food']
        }
        
        result = api._format_product(product_data, '123456')
        assert result['product_name'] == 'Test Product'
        assert result['barcode'] == '123456'
        assert result['category'] == 'Food'