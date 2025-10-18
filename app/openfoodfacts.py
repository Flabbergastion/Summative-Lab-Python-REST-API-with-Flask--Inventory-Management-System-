"""OpenFoodFacts API Integration"""

import requests

class OpenFoodFactsAPI:
    """Client for OpenFoodFacts API"""
    
    def __init__(self, base_url="https://world.openfoodfacts.org/api/v2"):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'User-Agent': 'InventoryManagementSystem/1.0',
            'Accept': 'application/json'
        }
    
    def get_product_by_barcode(self, barcode):
        """Fetch product by barcode"""
        try:
            response = requests.get(f"{self.base_url}/product/{barcode}", 
                                    headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 1 and 'product' in data:
                    return self._format_product(data['product'], barcode)
        except:
            pass
        return None
    
    def search_products(self, search_term, page_size=20):
        """Search products by name"""
        try:
            params = {
                'search_terms': search_term,
                'page_size': min(page_size, 100),
                'json': 1
            }
            response = requests.get(f"{self.base_url}/search", 
                                    params=params, headers=self.headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                products = []
                for product in data.get('products', []):
                    formatted = self._format_product(product, product.get('code', ''))
                    if formatted:
                        products.append(formatted)
                return products
        except:
            pass
        return []
    
    def _format_product(self, product, barcode):
        """Format product data for inventory"""
        name = product.get('product_name')
        if not name or name == 'Unknown Product':
            return None
        
        # Get category
        category = 'Food & Beverage'
        for field in ['categories_tags', 'categories']:
            if product.get(field):
                categories = product[field]
                if isinstance(categories, list) and categories:
                    category = categories[-1].split(':', 1)[-1].replace('-', ' ').title()
                elif isinstance(categories, str):
                    category = categories.replace('-', ' ').title()
                break
        
        # Get allergens
        allergens = 'Not specified'
        for field in ['allergens_tags', 'allergens']:
            if product.get(field):
                allergen_list = product[field]
                if isinstance(allergen_list, list) and allergen_list:
                    allergens = ', '.join([a.split(':', 1)[-1].replace('-', ' ').title() for a in allergen_list])
                elif isinstance(allergen_list, str):
                    allergens = allergen_list.replace('-', ' ').title()
                break
        
        return {
            'product_name': name,
            'brands': product.get('brands', 'Unknown Brand'),
            'barcode': barcode,
            'category': category,
            'ingredients_text': product.get('ingredients_text', 'Not specified'),
            'nutrition_grades': product.get('nutrition_grades', 'unknown'),
            'allergens': allergens
        }