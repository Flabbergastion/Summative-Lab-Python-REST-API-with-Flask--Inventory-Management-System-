"""Flask REST API Routes for Inventory Management"""

from flask import Blueprint, request, jsonify
from app.database import inventory_db
from app.openfoodfacts import OpenFoodFactsAPI

api_bp = Blueprint('api', __name__)
openfoodfacts_api = OpenFoodFactsAPI()

def json_response(data=None, error=None, message=None, status=200):
    """Helper function for consistent JSON responses"""
    response = {'success': error is None}
    if data is not None: response['data'] = data
    if error: response['error'] = error
    if message: response['message'] = message
    return jsonify(response), status

@api_bp.route('/inventory', methods=['GET'])
def get_all_inventory():
    """GET /api/inventory - List all items with optional filters"""
    try:
        items = inventory_db.get_all_items(
            category=request.args.get('category'),
            search=request.args.get('search')
        )
        return json_response(data=items)
    except Exception as e:
        return json_response(error=str(e), status=500)

@api_bp.route('/inventory/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    """GET /api/inventory/<id> - Get specific item"""
    try:
        item = inventory_db.get_item_by_id(item_id)
        if not item:
            return json_response(error='Item not found', status=404)
        return json_response(data=item)
    except Exception as e:
        return json_response(error=str(e), status=500)

@api_bp.route('/inventory', methods=['POST'])
def create_inventory_item():
    """POST /api/inventory - Create new item"""
    try:
        if not request.is_json:
            return json_response(error='Content-Type must be application/json', status=400)
        
        try:
            data = request.get_json()
        except Exception:
            return json_response(error='Invalid JSON format', status=400)
            
        if not data:
            return json_response(error='Request body cannot be empty', status=400)
            
        for field in ['product_name', 'brands']:
            if not data.get(field):
                return json_response(error=f'Missing required field: {field}', status=400)
        
        new_item = inventory_db.create_item(data)
        return json_response(data=new_item, message='Item created successfully', status=201)
    except Exception as e:
        return json_response(error=str(e), status=500)

@api_bp.route('/inventory/<int:item_id>', methods=['PATCH'])
def update_inventory_item(item_id):
    """PATCH /api/inventory/<id> - Update item"""
    try:
        if not request.is_json:
            return json_response(error='Content-Type must be application/json', status=400)
        
        updated_item = inventory_db.update_item(item_id, request.get_json())
        if not updated_item:
            return json_response(error='Item not found', status=404)
        return json_response(data=updated_item, message='Item updated successfully')
    except Exception as e:
        return json_response(error=str(e), status=500)

@api_bp.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    """DELETE /api/inventory/<id> - Delete item"""
    try:
        if not inventory_db.delete_item(item_id):
            return json_response(error='Item not found', status=404)
        return json_response(message='Item deleted successfully')
    except Exception as e:
        return json_response(error=str(e), status=500)

@api_bp.route('/inventory/fetch', methods=['POST'])
def fetch_product_from_external_api():
    """POST /api/inventory/fetch - Fetch from OpenFoodFacts"""
    try:
        if not request.is_json:
            return json_response(error='Content-Type must be application/json', status=400)
        
        data = request.get_json()
        product_data = None
        
        if data.get('barcode'):
            product_data = openfoodfacts_api.get_product_by_barcode(data['barcode'])
        elif data.get('search'):
            products = openfoodfacts_api.search_products(data['search'])
            product_data = products[0] if products else None
        else:
            return json_response(error='Either barcode or search parameter is required', status=400)
        
        if not product_data:
            return json_response(error='Product not found in external API', status=404)
        return json_response(data=product_data, message='Product data fetched successfully')
    except Exception as e:
        return json_response(error=str(e), status=500)

@api_bp.route('/inventory/fetch-and-add', methods=['POST'])
def fetch_and_add_product():
    """POST /api/inventory/fetch-and-add - Fetch and add to inventory"""
    try:
        if not request.is_json:
            return json_response(error='Content-Type must be application/json', status=400)
        
        data = request.get_json()
        if not data.get('barcode'):
            return json_response(error='Barcode is required', status=400)
        
        if inventory_db.get_by_barcode(data['barcode']):
            return json_response(error='Product with this barcode already exists', status=409)
        
        product_data = openfoodfacts_api.get_product_by_barcode(data['barcode'])
        if not product_data:
            return json_response(error='Product not found in external API', status=404)
        
        product_data.update({
            'quantity': data.get('quantity', 0),
            'price': data.get('price', 0.0)
        })
        
        new_item = inventory_db.create_item(product_data)
        return json_response(data=new_item, message='Product fetched and added to inventory', status=201)
    except Exception as e:
        return json_response(error=str(e), status=500)