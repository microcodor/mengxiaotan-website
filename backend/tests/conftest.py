"""
Pytest configuration and fixtures for tests
"""

import os
import sys
import pytest
import tempfile

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


@pytest.fixture
def app():
    """Create Flask app for testing"""
    from app import create_app
    from app import db
    
    # Create temporary directory for uploads
    temp_upload_dir = tempfile.mkdtemp()
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['UPLOAD_FOLDER'] = temp_upload_dir
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    # Cleanup temp directory
    import shutil
    if os.path.exists(temp_upload_dir):
        shutil.rmtree(temp_upload_dir)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create database session for testing"""
    from app import db
    
    with app.app_context():
        yield db.session
