"""Configuration"""
import os

class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    TESTING = os.getenv('FLASK_TESTING', 'False').lower() == 'true'
    OPENFOODFACTS_BASE_URL = "https://world.openfoodfacts.org/api/v2"