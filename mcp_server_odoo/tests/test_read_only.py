import unittest
from unittest.mock import MagicMock, patch
import os
import asyncio
import sys

# Add the project root to the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set dummy env vars to avoid KeyError during import
os.environ["ODOO_URL"] = "http://localhost:8069"
os.environ["ODOO_DB"] = "test_db"
os.environ["ODOO_USERNAME"] = "admin"
os.environ["ODOO_PASSWORD"] = "admin"

from mcp_server_odoo.server import list_tools, get_odoo_client, odoo_client
from mcp_server_odoo.odoo_client import OdooConfig

class TestReadOnlyMode(unittest.TestCase):
    def setUp(self):
        # Reset global client
        import mcp_server_odoo.server
        mcp_server_odoo.server.odoo_client = None

    @patch.dict(os.environ, {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "test_db",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin",
        "ODOO_READ_ONLY": "false"
    })
    def test_read_write_mode(self):
        """Test that all tools are available in read-write mode"""
        # Mock OdooClient to avoid actual connection
        with patch('mcp_server_odoo.server.OdooClient') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.config = OdooConfig(
                url="http://localhost:8069",
                database="test_db",
                username="admin",
                password="admin"
            )
            
            # Get tools
            tools = asyncio.run(list_tools())
            tool_names = [t.name for t in tools]
            
            # Verify modification tools are present
            self.assertIn("create_record", tool_names)
            self.assertIn("update_record", tool_names)
            self.assertIn("delete_record", tool_names)

    @patch.dict(os.environ, {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "test_db",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin",
        "ODOO_READ_ONLY": "true"
    })
    def test_read_only_mode(self):
        """Test that modification tools are hidden in read-only mode"""
        # Mock OdooClient
        with patch('mcp_server_odoo.server.OdooClient') as MockClient:
            mock_instance = MockClient.return_value
            # Manually set read_only since we haven't implemented it in OdooConfig yet
            # This test will fail until we implement the changes, which is expected
            mock_instance.config = MagicMock()
            # We expect the code to check this attribute
            mock_instance.config.read_only = True
            
            # Get tools
            tools = asyncio.run(list_tools())
            tool_names = [t.name for t in tools]
            
            # Verify modification tools are ABSENT
            self.assertNotIn("create_record", tool_names)
            self.assertNotIn("update_record", tool_names)
            self.assertNotIn("delete_record", tool_names)
            
            # Verify read tools are PRESENT
            self.assertIn("search_records", tool_names)
            self.assertIn("get_record", tool_names)
            self.assertIn("list_models", tool_names)

if __name__ == '__main__':
    unittest.main()
