"""Unit Tests for CLI"""

import pytest
from unittest.mock import patch, Mock
import sys
import os
from click.testing import CliRunner

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.inventory_cli import cli

@pytest.fixture
def runner():
    return CliRunner()

class TestCLI:
    """CLI tests"""
    
    @patch('cli.inventory_cli.cli_instance')
    def test_list_command(self, mock_cli_instance, runner):
        """Test list command"""
        mock_cli_instance.db.get_all_items.return_value = [
            {'id': 1, 'name': 'Test', 'category': 'Food', 'quantity': 5, 'price': 10.0}
        ]
        
        def mock_display_table(items):
            for item in items:
                print(item['name'])  # Print the name so our test can find it
        mock_cli_instance.display_items_table = mock_display_table
        
        result = runner.invoke(cli, ['list'])
        assert result.exit_code == 0
        assert 'Test' in result.output
    
    @patch('cli.inventory_cli.cli_instance')  
    def test_get_command(self, mock_cli_instance, runner):
        """Test get command"""
        mock_cli_instance.db.get_item_by_id.return_value = {
            'id': 1, 'name': 'Test Item', 'category': 'Food'
        }
        
        def mock_display_item(item):
            print(f"Name: {item['name']}")  # Print the name so our test can find it
        mock_cli_instance.display_item = mock_display_item
        
        result = runner.invoke(cli, ['get', '1'])
        assert result.exit_code == 0
        assert 'Test Item' in result.output
    
    @patch('cli.inventory_cli.cli_instance')
    def test_add_command(self, mock_cli_instance, runner):
        """Test add command with input"""
        mock_cli_instance.db.create_item.return_value = {
            'id': 1, 'name': 'New Item'
        }
        
        # Simulate user input
        input_data = 'Test Item\nFood\n5\n10.0\nTest description\n\n'
        result = runner.invoke(cli, ['add'], input=input_data)
        assert result.exit_code == 0
    
    @patch('cli.inventory_cli.cli_instance')
    def test_lookup_command(self, mock_cli_instance, runner):
        """Test barcode lookup"""
        mock_cli_instance.openfoodfacts.get_product_by_barcode.return_value = {
            'name': 'Found Product',
            'brands': 'Test Brand'
        }
        
        result = runner.invoke(cli, ['lookup', '123456789'], input='n\n')
        assert result.exit_code == 0
        assert 'Found Product' in result.output
    
    @patch('cli.inventory_cli.cli_instance')
    def test_stats_command(self, mock_cli_instance, runner):
        """Test stats command"""
        mock_cli_instance.db.get_all_items.return_value = [
            {'id': 1, 'category': 'Food', 'quantity': 5, 'price': 10.0}
        ]
        
        result = runner.invoke(cli, ['stats'])
        assert result.exit_code == 0
        assert 'Statistics' in result.output