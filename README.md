# Inventory Management System

Flask REST API with OpenFoodFacts integration and CLI interface.

## Features

- REST API with CRUD operations
- OpenFoodFacts product data integration
- Command-line interface
- Complete test suite

## Quick Start

```bash
# Install
pip install flask flask-cors click requests pytest

# Run API
python run.py

# Use CLI
python cli_main.py list
```

## API Endpoints

Base: `http://localhost:5000/api`

- `GET /inventory` - List items
- `POST /inventory` - Create item
- `PUT /inventory/<id>` - Update item  
- `DELETE /inventory/<id>` - Delete item
- `GET /external/product/<barcode>` - Fetch product data

## CLI Commands

```bash
python cli_main.py list
python cli_main.py add
python cli_main.py lookup <barcode>
python cli_main.py stats
```

## Testing

```bash
pytest
```