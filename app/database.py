"""Simplified inventory database using array-based storage"""

from datetime import datetime
from typing import List, Dict, Optional

# Sample inventory data
INVENTORY_DATA = [
    {"id": 1, "product_name": "Organic Almond Milk", "brands": "Silk", "quantity": 25, "price": 4.99, "barcode": "025293600218", "category": "Plant-based Milk"},
    {"id": 2, "product_name": "Whole Grain Bread", "brands": "Dave's Killer Bread", "quantity": 12, "price": 5.49, "barcode": "013570334215", "category": "Bread"},
    {"id": 3, "product_name": "Greek Yogurt", "brands": "Chobani", "quantity": 30, "price": 1.99, "barcode": "894700010045", "category": "Dairy"},
    {"id": 4, "product_name": "Dark Chocolate Bar", "brands": "Lindt", "quantity": 18, "price": 3.99, "barcode": "037466010014", "category": "Chocolate"},
    {"id": 5, "product_name": "Organic Bananas", "brands": "Dole", "quantity": 50, "price": 0.79, "barcode": "011111021020", "category": "Fresh Fruit"}
]

class InventoryDatabase:
    """Simple in-memory database for inventory management"""
    
    def __init__(self):
        self.data = INVENTORY_DATA.copy()
        self._next_id = max([item['id'] for item in self.data], default=0) + 1
    
    def get_all_items(self, category=None, search=None):
        """Get all items with optional filtering"""
        items = self.data
        if category:
            items = [item for item in items if item.get('category', '').lower() == category.lower()]
        if search:
            search = search.lower()
            items = [item for item in items if search in item.get('product_name', '').lower() or search in item.get('brands', '').lower()]
        return items
    
    def get_item_by_id(self, item_id):
        """Get item by ID"""
        return next((item for item in self.data if item['id'] == item_id), None)
    
    def create_item(self, item_data):
        """Add new item"""
        item = {**item_data, 'id': self._next_id, 'quantity': item_data.get('quantity', 0), 'price': item_data.get('price', 0.0)}
        self.data.append(item)
        self._next_id += 1
        return item
    
    def update_item(self, item_id, update_data):
        """Update existing item"""
        for i, item in enumerate(self.data):
            if item['id'] == item_id:
                self.data[i] = {**item, **update_data, 'id': item_id}
                return self.data[i]
        return None
    
    def delete_item(self, item_id):
        """Delete item by ID"""
        for i, item in enumerate(self.data):
            if item['id'] == item_id:
                del self.data[i]
                return True
        return False
    
    def get_by_barcode(self, barcode):
        """Get item by barcode"""
        return next((item for item in self.data if item.get('barcode') == barcode), None)

inventory_db = InventoryDatabase()