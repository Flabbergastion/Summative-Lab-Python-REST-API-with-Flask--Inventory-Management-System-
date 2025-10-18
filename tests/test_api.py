"""Unit Tests for Flask API"""

import pytest
import json
from unittest.mock import patch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import InventoryDatabase

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
def client(app):
    return app.test_client()

class TestAPI:
    """Core API tests"""
    
    def test_health_check(self, client):
        """Test health endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_crud_operations(self, client):
        """Test complete CRUD workflow"""
        # Create
        item_data = {'product_name': 'Test', 'brands': 'TestBrand', 'quantity': 5, 'price': 10.0}
        response = client.post('/api/inventory', 
                               data=json.dumps(item_data),
                               content_type='application/json')
        assert response.status_code == 201
        created = json.loads(response.data)['data']
        item_id = created['id']
        
        # Read
        response = client.get(f'/api/inventory/{item_id}')
        assert response.status_code == 200
        
        # Update
        update_data = {'product_name': 'Updated', 'brands': 'UpdatedBrand', 'quantity': 10}
        response = client.patch(f'/api/inventory/{item_id}',
                              data=json.dumps(update_data),
                              content_type='application/json')
        assert response.status_code == 200        # Delete
        response = client.delete(f'/api/inventory/{item_id}')
        assert response.status_code == 200
        
        # Verify deleted
        response = client.get(f'/api/inventory/{item_id}')
        assert response.status_code == 404
    
    def test_error_handling(self, client):
        """Test error scenarios"""
        # Invalid JSON
        response = client.post('/api/inventory', 
                               data='invalid',
                               content_type='application/json')
        assert response.status_code == 400
        
        # Missing required fields
        response = client.post('/api/inventory', 
                               data=json.dumps({'product_name': 'test'}),  # Missing brands
                               content_type='application/json')
        assert response.status_code == 400
        
        # Not found
        response = client.get('/api/inventory/99999')
        assert response.status_code == 404
    
    @patch('app.openfoodfacts.OpenFoodFactsAPI.get_product_by_barcode')
    def test_external_api(self, mock_api, client):
        """Test OpenFoodFacts integration"""
        mock_api.return_value = {
            'product_name': 'Mock Product',
            'brands': 'Mock Brand',
            'barcode': '123456'
        }
        
        response = client.post('/api/inventory/fetch', 
                               data=json.dumps({'barcode': '123456'}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['product_name'] == 'Mock Product'
    
    @patch('app.openfoodfacts.OpenFoodFactsAPI.search_products')
    def test_search(self, mock_search, client):
        """Test product search"""
        mock_search.return_value = [{'product_name': 'Result'}]
        
        response = client.post('/api/inventory/fetch', 
                               data=json.dumps({'search': 'test'}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['product_name'] == 'Result'

class TestInventoryDatabase:
    """Test suite for the inventory database class"""
    
    def test_database_initialization(self):
        """Test database initialization"""
        db = InventoryDatabase()
        assert len(db.data) > 0
        assert db._next_id > 0
    
    def test_get_all_items(self):
        """Test get_all_items method"""
        db = InventoryDatabase()
        items = db.get_all_items()
        assert isinstance(items, list)
        assert len(items) > 0
    
    def test_get_item_by_id(self):
        """Test get_item_by_id method"""
        db = InventoryDatabase()
        item = db.get_item_by_id(1)
        assert item is not None
        assert item['id'] == 1
        
        # Test non-existent ID
        item = db.get_item_by_id(999)
        assert item is None
    
    def test_create_item(self):
        """Test create_item method"""
        db = InventoryDatabase()
        initial_count = len(db.data)
        
        new_item_data = {
            'product_name': 'New Test Product',
            'brands': 'New Test Brand'
        }
        
        created_item = db.create_item(new_item_data)
        
        assert len(db.data) == initial_count + 1
        assert created_item['product_name'] == new_item_data['product_name']
        assert 'id' in created_item
        # Remove check for 'created_at' field since we simplified the database
    
    def test_update_item(self):
        """Test update_item method"""
        db = InventoryDatabase()
        
        update_data = {
            'quantity': 100,
            'price': 9.99
        }
        
        updated_item = db.update_item(1, update_data)
        
        assert updated_item is not None
        assert updated_item['quantity'] == 100
        assert updated_item['price'] == 9.99
        assert updated_item['id'] == 1
        
        # Test non-existent ID
        result = db.update_item(999, update_data)
        assert result is None
    
    def test_delete_item(self):
        """Test delete_item method"""
        db = InventoryDatabase()
        
        # Create an item to delete
        new_item = db.create_item({
            'product_name': 'Delete Me',
            'brands': 'Delete Brand'
        })
        item_id = new_item['id']
        initial_count = len(db.data)
        
        # Delete the item
        success = db.delete_item(item_id)
        
        assert success is True
        assert len(db.data) == initial_count - 1
        assert db.get_item_by_id(item_id) is None
        
        # Test deleting non-existent item
        success = db.delete_item(999)
        assert success is False
    
    def test_get_by_barcode(self):
        """Test get_by_barcode method"""
        db = InventoryDatabase()
        
        # Test with existing barcode
        item = db.get_by_barcode('025293600218')  # From our sample data
        assert item is not None
        assert item['barcode'] == '025293600218'
        
        # Test with non-existent barcode
        item = db.get_by_barcode('0000000000000')
        assert item is None