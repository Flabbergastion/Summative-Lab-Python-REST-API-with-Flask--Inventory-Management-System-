"""Inventory Management CLI"""

import click
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import InventoryDatabase
from app.openfoodfacts import OpenFoodFactsAPI

class InventoryCLI:
    """CLI for Inventory Management System"""
    
    def __init__(self):
        self.db = InventoryDatabase()
        self.openfoodfacts = OpenFoodFactsAPI()
    
    def display_item(self, item):
        """Display single item"""
        print(f"\nID: {item.get('id', 'N/A')}")
        print(f"Name: {item.get('name', 'N/A')}")
        print(f"Category: {item.get('category', 'N/A')}")
        print(f"Quantity: {item.get('quantity', 'N/A')}")
        print(f"Price: ${item.get('price', 'N/A')}")
        print(f"Description: {item.get('description', 'N/A')}")
        if 'barcode' in item:
            print(f"Barcode: {item['barcode']}")
        if 'brands' in item:
            print(f"Brand: {item['brands']}")
        print("-" * 50)
    
    def display_items_table(self, items):
        """Display items in table format"""
        if not items:
            print("No items found.")
            return
        
        print(f"{'ID':<5} {'Name':<30} {'Category':<20} {'Quantity':<10} {'Price':<10}")
        print("-" * 75)
        
        for item in items:
            print(f"{str(item.get('id', 'N/A'))[:4]:<5} "
                  f"{str(item.get('name', 'N/A'))[:29]:<30} "
                  f"{str(item.get('category', 'N/A'))[:19]:<20} "
                  f"{str(item.get('quantity', 'N/A'))[:9]:<10} "
                  f"${item.get('price', 'N/A')}"[:9])

# CLI commands
@click.group()
def cli():
    """Inventory Management System CLI"""
    pass

cli_instance = InventoryCLI()

@cli.command()
def list():
    """List all items"""
    items = cli_instance.db.get_all_items()
    print(f"\n📦 Inventory Items ({len(items)} total)")
    print("=" * 50)
    cli_instance.display_items_table(items)

@cli.command()
@click.argument('item_id', type=int)
def get(item_id):
    """Get item by ID"""
    item = cli_instance.db.get_item_by_id(item_id)
    if item:
        print(f"\n📦 Item Details")
        cli_instance.display_item(item)
    else:
        print(f"❌ Item {item_id} not found.")

@cli.command()
def add():
    """Add new item"""
    try:
        print("\n📝 Adding New Item")
        print("=" * 20)
        
        name = click.prompt("Name", type=str)
        category = click.prompt("Category", type=str)
        quantity = click.prompt("Quantity", type=int, default=1)
        price = click.prompt("Price", type=float, default=0.0)
        description = click.prompt("Description", type=str, default="")
        
        barcode = click.prompt("Barcode (optional)", type=str, default="", show_default=False)
        
        item_data = {
            'name': name, 'category': category, 'quantity': quantity,
            'price': price, 'description': description
        }
        
        if barcode:
            item_data['barcode'] = barcode
            print(f"Fetching data for {barcode}...")
            openfood_data = cli_instance.openfoodfacts.get_product_by_barcode(barcode)
            if openfood_data:
                print("✓ Product data found!")
                for key, value in openfood_data.items():
                    if key not in item_data or not item_data[key]:
                        item_data[key] = value
        
        new_item = cli_instance.db.create_item(item_data)
        if new_item:
            print("\n✅ Item added!")
            cli_instance.display_item(new_item)
        else:
            print("❌ Failed to add item.")
    except click.Abort:
        print("\nCancelled.")

@cli.command()
@click.argument('item_id', type=int)
def update(item_id):
    """Update item"""
    existing = cli_instance.db.get_item_by_id(item_id)
    if not existing:
        print(f"❌ Item {item_id} not found.")
        return
    
    try:
        print(f"\n📝 Updating Item {item_id}")
        
        item_data = {
            'name': click.prompt("Name", default=existing.get('name', '')),
            'category': click.prompt("Category", default=existing.get('category', '')),
            'quantity': click.prompt("Quantity", type=int, default=existing.get('quantity', 1)),
            'price': click.prompt("Price", type=float, default=existing.get('price', 0.0)),
            'description': click.prompt("Description", default=existing.get('description', ''))
        }
        
        updated = cli_instance.db.update_item(item_id, item_data)
        if updated:
            print("\n✅ Item updated!")
            cli_instance.display_item(updated)
    except click.Abort:
        print("\nCancelled.")

@cli.command()
@click.argument('item_id', type=int)
@click.confirmation_option(prompt='Delete this item?')
def delete(item_id):
    """Delete item"""
    if cli_instance.db.delete_item(item_id):
        print("✅ Item deleted!")
    else:
        print(f"❌ Item {item_id} not found.")

@cli.command()
@click.argument('barcode')
def lookup(barcode):
    """Lookup product by barcode"""
    print(f"\n🔍 Looking up {barcode}")
    
    product = cli_instance.openfoodfacts.get_product_by_barcode(barcode)
    if product:
        print("✅ Product found!")
        for key, value in product.items():
            if key != 'id':
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        if click.confirm("\nAdd to inventory?"):
            quantity = click.prompt("Quantity", type=int, default=1)
            price = click.prompt("Price", type=float, default=0.0)
            
            item_data = product.copy()
            item_data.update({
                'quantity': quantity, 'price': price,
                'name': product.get('product_name', 'Unknown')
            })
            
            new_item = cli_instance.db.create_item(item_data)
            if new_item:
                print("\n✅ Added to inventory!")
    else:
        print(f"❌ Product {barcode} not found.")

@cli.command()
@click.argument('search_term')
def search(search_term):
    """Search products"""
    print(f"\n🔍 Searching '{search_term}'")
    
    products = cli_instance.openfoodfacts.search_products(search_term)
    if products:
        print(f"✅ Found {len(products)} products:")
        for i, product in enumerate(products[:10], 1):
            print(f"{i}. {product.get('product_name', 'Unknown')}")
            print(f"   Brand: {product.get('brands', 'Unknown')}")
            if product.get('barcode'):
                print(f"   Barcode: {product['barcode']}")
            print()
    else:
        print(f"❌ No products found for '{search_term}'")

@cli.command()
def stats():
    """Show inventory statistics"""
    items = cli_instance.db.get_all_items()
    if not items:
        print("📊 Inventory is empty.")
        return
    
    total_items = len(items)
    total_quantity = sum(item.get('quantity', 0) for item in items)
    total_value = sum(item.get('quantity', 0) * item.get('price', 0) for item in items)
    
    categories = {}
    for item in items:
        cat = item.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📊 Inventory Statistics")
    print("=" * 25)
    print(f"Total Items: {total_items}")
    print(f"Total Quantity: {total_quantity}")
    print(f"Total Value: ${total_value:.2f}")
    
    print(f"\n📂 Categories:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} items")

