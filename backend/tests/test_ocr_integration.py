"""
Integration tests for OCR payment information extraction

Tests the complete flow from file upload to OCR extraction and storage.
"""

import pytest
from io import BytesIO
from app.models import Order, User, SubscriptionPlan
from app import db


class TestOCRIntegration:
    """Integration tests for OCR functionality"""
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def auth_headers(self, app, client):
        """Create authenticated user and return JWT token"""
        with app.app_context():
            # Create test user
            user = User(
                username='testuser',
                email='test@example.com',
                phone='13800138000'
            )
            user.set_password('password123')
            db.session.add(user)
            
            # Create subscription plan
            plan = SubscriptionPlan(
                name='标准版',
                price=299.00,
                duration_days=30,
                level='standard'
            )
            db.session.add(plan)
            db.session.commit()
            
            # Create order
            order = Order(
                order_no='TEST20240115001',
                user_id=user.id,
                plan_id=plan.id,
                amount=299.00,
                payment_method='offline',
                payment_status='pending'
            )
            db.session.add(order)
            db.session.commit()
            
            # Login to get token
            response = client.post('/api/auth/login', json={
                'username': 'testuser',
                'password': 'password123'
            })
            
            token = response.json['data']['access_token']
            
            return {
                'Authorization': f'Bearer {token}'
            }, user.id, order.id
    
    def test_upload_payment_proof_stores_ocr_result(self, app, client, auth_headers, monkeypatch):
        """Test that OCR result is stored in Order.payment_info"""
        headers, user_id, order_id = auth_headers
        
        with app.app_context():
            # Mock OCR extraction to return a result
            from app.services.payment_proof_manager import PaymentProofManager
            
            mock_ocr_result = {
                'amount': 299.00,
                'transaction_id': '20240115123456789012',
                'timestamp': '2024-01-15 10:30:00',
                'confidence': 0.95,
                'ocr_provider': 'baidu',
                'extracted_at': '2024-01-15T10:31:00'
            }
            
            original_extract = PaymentProofManager.extract_payment_info
            
            def mock_extract(self, file_path):
                return mock_ocr_result
            
            monkeypatch.setattr(PaymentProofManager, 'extract_payment_info', mock_extract)
            
            # Upload file
            data = {
                'file': (BytesIO(b'fake image content'), 'test.jpg')
            }
            
            response = client.post(
                f'/api/subscriptions/orders/{order_id}/payment-proof',
                data=data,
                headers=headers,
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 200
            assert response.json['success'] is True
            assert 'ocr_result' in response.json['data']
            assert response.json['data']['ocr_result']['amount'] == 299.00
            
            # Verify OCR result is stored in database
            order = Order.query.get(order_id)
            assert order.payment_info is not None
            assert order.payment_info['amount'] == 299.00
            assert order.payment_info['transaction_id'] == '20240115123456789012'
            assert order.payment_info['ocr_provider'] == 'baidu'
    
    def test_upload_payment_proof_ocr_silent_failure(self, app, client, auth_headers, monkeypatch):
        """Test that upload succeeds even when OCR fails"""
        headers, user_id, order_id = auth_headers
        
        with app.app_context():
            # Mock OCR extraction to raise an exception
            from app.services.payment_proof_manager import PaymentProofManager
            
            def mock_extract(self, file_path):
                raise Exception("OCR API failed")
            
            monkeypatch.setattr(PaymentProofManager, 'extract_payment_info', mock_extract)
            
            # Upload file
            data = {
                'file': (BytesIO(b'fake image content'), 'test.jpg')
            }
            
            response = client.post(
                f'/api/subscriptions/orders/{order_id}/payment-proof',
                data=data,
                headers=headers,
                content_type='multipart/form-data'
            )
            
            # Upload should still succeed
            assert response.status_code == 200
            assert response.json['success'] is True
            assert 'file_url' in response.json['data']
            
            # OCR result should not be in response
            assert 'ocr_result' not in response.json['data']
            
            # Verify payment_info is None in database
            order = Order.query.get(order_id)
            assert order.payment_info is None
    
    def test_upload_payment_proof_no_ocr_keys(self, app, client, auth_headers, monkeypatch):
        """Test upload when OCR API keys are not configured"""
        headers, user_id, order_id = auth_headers
        
        with app.app_context():
            # Mock config to have no API keys
            monkeypatch.setitem(app.config, 'BAIDU_OCR_API_KEY', '')
            monkeypatch.setitem(app.config, 'BAIDU_OCR_SECRET_KEY', '')
            
            # Upload file
            data = {
                'file': (BytesIO(b'fake image content'), 'test.jpg')
            }
            
            response = client.post(
                f'/api/subscriptions/orders/{order_id}/payment-proof',
                data=data,
                headers=headers,
                content_type='multipart/form-data'
            )
            
            # Upload should succeed
            assert response.status_code == 200
            assert response.json['success'] is True
            
            # OCR result should not be present
            assert 'ocr_result' not in response.json['data']
