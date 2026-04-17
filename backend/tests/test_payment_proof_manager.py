"""
Unit tests for PaymentProofManager

Tests file upload validation, storage, and error handling.
"""

import os
import pytest
import tempfile
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app.services.payment_proof_manager import PaymentProofManager


class TestPaymentProofManager:
    """Test suite for PaymentProofManager"""
    
    @pytest.fixture
    def manager(self, app):
        """Create PaymentProofManager instance"""
        with app.app_context():
            return PaymentProofManager()
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        return app
    
    def create_file_storage(self, filename, content=b'test content', mimetype='image/jpeg'):
        """Helper to create FileStorage object"""
        return FileStorage(
            stream=BytesIO(content),
            filename=filename,
            content_type=mimetype
        )
    
    # Test validate_file method
    
    def test_validate_file_jpg_success(self, manager):
        """Test validation succeeds for JPG files"""
        file = self.create_file_storage('test.jpg', b'x' * 1024, 'image/jpeg')
        is_valid, error = manager.validate_file(file)
        assert is_valid is True
        assert error == ""
    
    def test_validate_file_png_success(self, manager):
        """Test validation succeeds for PNG files"""
        file = self.create_file_storage('test.png', b'x' * 1024, 'image/png')
        is_valid, error = manager.validate_file(file)
        assert is_valid is True
        assert error == ""
    
    def test_validate_file_pdf_success(self, manager):
        """Test validation succeeds for PDF files"""
        file = self.create_file_storage('test.pdf', b'x' * 1024, 'application/pdf')
        is_valid, error = manager.validate_file(file)
        assert is_valid is True
        assert error == ""
    
    def test_validate_file_unsupported_extension(self, manager):
        """Test validation fails for unsupported file extensions"""
        file = self.create_file_storage('test.txt', b'test', 'text/plain')
        is_valid, error = manager.validate_file(file)
        assert is_valid is False
        assert "不支持的文件格式" in error
    
    def test_validate_file_unsupported_mimetype(self, manager):
        """Test validation fails for unsupported MIME types"""
        file = self.create_file_storage('test.jpg', b'test', 'text/plain')
        is_valid, error = manager.validate_file(file)
        assert is_valid is False
        assert "不支持的文件类型" in error
    
    def test_validate_file_too_large(self, manager):
        """Test validation fails for files larger than 5MB"""
        # Create a file larger than 5MB
        large_content = b'x' * (6 * 1024 * 1024)
        file = self.create_file_storage('test.jpg', large_content, 'image/jpeg')
        is_valid, error = manager.validate_file(file)
        assert is_valid is False
        assert "文件大小超过5MB限制" in error
    
    def test_validate_file_exactly_5mb(self, manager):
        """Test validation succeeds for files exactly 5MB"""
        # Create a file exactly 5MB
        content = b'x' * (5 * 1024 * 1024)
        file = self.create_file_storage('test.jpg', content, 'image/jpeg')
        is_valid, error = manager.validate_file(file)
        assert is_valid is True
        assert error == ""
    
    def test_validate_file_just_under_5mb(self, manager):
        """Test validation succeeds for files just under 5MB"""
        # Create a file just under 5MB (4.9MB)
        content = b'x' * int(4.9 * 1024 * 1024)
        file = self.create_file_storage('test.jpg', content, 'image/jpeg')
        is_valid, error = manager.validate_file(file)
        assert is_valid is True
        assert error == ""
    
    def test_validate_file_empty(self, manager):
        """Test validation fails for empty files"""
        file = self.create_file_storage('test.jpg', b'', 'image/jpeg')
        is_valid, error = manager.validate_file(file)
        assert is_valid is False
        assert "文件为空" in error
    
    def test_validate_file_no_filename(self, manager):
        """Test validation fails when no filename provided"""
        file = self.create_file_storage('', b'test', 'image/jpeg')
        is_valid, error = manager.validate_file(file)
        assert is_valid is False
        assert "未选择文件" in error
    
    def test_validate_file_none(self, manager):
        """Test validation fails when file is None"""
        is_valid, error = manager.validate_file(None)
        assert is_valid is False
        assert "未选择文件" in error
    
    # Test upload_proof method
    
    def test_upload_proof_success(self, manager, app):
        """Test successful file upload"""
        with app.app_context():
            file = self.create_file_storage('test.jpg', b'test content', 'image/jpeg')
            order_id = 123
            
            result = manager.upload_proof(file, order_id)
            
            assert result['success'] is True
            assert 'file_url' in result
            assert '/uploads/payment_proofs/' in result['file_url']
            assert f'{order_id}_' in result['file_url']
            assert result['file_url'].endswith('.jpg')
    
    def test_upload_proof_creates_directory_structure(self, manager, app):
        """Test that upload creates year/month directory structure"""
        with app.app_context():
            file = self.create_file_storage('test.jpg', b'test content', 'image/jpeg')
            order_id = 456
            
            result = manager.upload_proof(file, order_id)
            
            assert result['success'] is True
            
            # Check directory structure exists
            from datetime import datetime
            year = datetime.now().strftime('%Y')
            month = datetime.now().strftime('%m')
            expected_dir = os.path.join(
                app.config['UPLOAD_FOLDER'],
                'payment_proofs',
                year,
                month
            )
            assert os.path.exists(expected_dir)
    
    def test_upload_proof_invalid_file(self, manager, app):
        """Test upload fails for invalid file"""
        with app.app_context():
            file = self.create_file_storage('test.txt', b'test', 'text/plain')
            order_id = 789
            
            result = manager.upload_proof(file, order_id)
            
            assert result['success'] is False
            assert 'error' in result
            assert "不支持的文件格式" in result['error']
    
    def test_upload_proof_file_too_large(self, manager, app):
        """Test upload fails for files larger than 5MB"""
        with app.app_context():
            large_content = b'x' * (6 * 1024 * 1024)
            file = self.create_file_storage('test.jpg', large_content, 'image/jpeg')
            order_id = 999
            
            result = manager.upload_proof(file, order_id)
            
            assert result['success'] is False
            assert 'error' in result
            assert "文件大小超过5MB限制" in result['error']
    
    def test_upload_proof_different_extensions(self, manager, app):
        """Test upload works for all supported extensions"""
        with app.app_context():
            test_cases = [
                ('test.jpg', 'image/jpeg', '.jpg'),
                ('test.jpeg', 'image/jpeg', '.jpeg'),
                ('test.png', 'image/png', '.png'),
                ('test.pdf', 'application/pdf', '.pdf'),
            ]
            
            for filename, mimetype, expected_ext in test_cases:
                file = self.create_file_storage(filename, b'test content', mimetype)
                order_id = 100
                
                result = manager.upload_proof(file, order_id)
                
                assert result['success'] is True
                assert result['file_url'].endswith(expected_ext)
    
    # Test helper methods
    
    def test_allowed_file_valid_extensions(self, manager):
        """Test _allowed_file returns True for valid extensions"""
        assert manager._allowed_file('test.jpg') is True
        assert manager._allowed_file('test.jpeg') is True
        assert manager._allowed_file('test.JPG') is True  # Case insensitive
        assert manager._allowed_file('test.png') is True
        assert manager._allowed_file('test.PNG') is True
        assert manager._allowed_file('test.pdf') is True
    
    def test_allowed_file_invalid_extensions(self, manager):
        """Test _allowed_file returns False for invalid extensions"""
        assert manager._allowed_file('test.txt') is False
        assert manager._allowed_file('test.doc') is False
        assert manager._allowed_file('test.exe') is False
        assert manager._allowed_file('test') is False  # No extension
    
    def test_get_file_extension(self, manager):
        """Test _get_file_extension extracts extension correctly"""
        assert manager._get_file_extension('test.jpg') == 'jpg'
        assert manager._get_file_extension('test.JPG') == 'jpg'  # Lowercase
        assert manager._get_file_extension('test.jpeg') == 'jpeg'
        assert manager._get_file_extension('test.png') == 'png'
        assert manager._get_file_extension('test.pdf') == 'pdf'
        assert manager._get_file_extension('test') == ''  # No extension
    
    def test_sanitize_filename(self, manager):
        """Test _sanitize_filename removes dangerous characters"""
        # This uses werkzeug.utils.secure_filename
        assert manager._sanitize_filename('test.jpg') == 'test.jpg'
        assert manager._sanitize_filename('../../../etc/passwd') == 'etc_passwd'
        assert manager._sanitize_filename('test file.jpg') == 'test_file.jpg'
    
    # Test OCR functionality
    
    def test_extract_payment_info_no_api_keys(self, manager, app, monkeypatch):
        """Test OCR extraction fails gracefully when API keys not configured"""
        with app.app_context():
            # Mock config to have no API keys
            monkeypatch.setattr(app.config, 'get', lambda key, default=None: {
                'OCR_PROVIDER': 'baidu',
                'BAIDU_OCR_API_KEY': '',
                'BAIDU_OCR_SECRET_KEY': ''
            }.get(key, default))
            
            result = manager.extract_payment_info('/fake/path.jpg')
            
            # Should return None when API keys not configured
            assert result is None
    
    def test_parse_ocr_result_with_amount(self, manager):
        """Test parsing OCR result extracts amount correctly"""
        words_result = [
            {'words': '支付金额: ¥299.00', 'probability': {'average': 0.95}},
            {'words': '其他文本', 'probability': {'average': 0.90}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        assert result['amount'] == 299.00
        assert result['ocr_provider'] == 'baidu'
        assert result['confidence'] > 0
    
    def test_parse_ocr_result_with_transaction_id(self, manager):
        """Test parsing OCR result extracts transaction ID correctly"""
        words_result = [
            {'words': '交易号: 20240115123456789012', 'probability': {'average': 0.92}},
            {'words': '其他文本', 'probability': {'average': 0.88}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        assert result['transaction_id'] == '20240115123456789012'
        assert result['ocr_provider'] == 'baidu'
    
    def test_parse_ocr_result_with_timestamp(self, manager):
        """Test parsing OCR result extracts timestamp correctly"""
        words_result = [
            {'words': '支付时间: 2024-01-15 10:30:00', 'probability': {'average': 0.93}},
            {'words': '其他文本', 'probability': {'average': 0.87}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        assert result['timestamp'] == '2024-01-15 10:30:00'
        assert result['ocr_provider'] == 'baidu'
    
    def test_parse_ocr_result_complete(self, manager):
        """Test parsing OCR result extracts all fields"""
        words_result = [
            {'words': '支付金额: ¥299.00', 'probability': {'average': 0.95}},
            {'words': '交易号: 20240115123456789012', 'probability': {'average': 0.92}},
            {'words': '支付时间: 2024-01-15 10:30:00', 'probability': {'average': 0.93}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        assert result['amount'] == 299.00
        assert result['transaction_id'] == '20240115123456789012'
        assert result['timestamp'] == '2024-01-15 10:30:00'
        assert result['ocr_provider'] == 'baidu'
        assert result['confidence'] > 0.9
        assert 'extracted_at' in result
    
    def test_parse_ocr_result_no_data(self, manager):
        """Test parsing OCR result returns None when no payment info found"""
        words_result = [
            {'words': '这是一些无关的文本', 'probability': {'average': 0.90}},
            {'words': '没有支付信息', 'probability': {'average': 0.88}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        # Should return None when no payment info extracted
        assert result is None
    
    def test_parse_ocr_result_various_amount_formats(self, manager):
        """Test parsing different amount formats"""
        test_cases = [
            ('金额: 299.00', 299.00),
            ('¥ 299.00', 299.00),
            ('299.00元', 299.00),
            ('实付: 299', 299.00),
            ('支付金额: 1999.99', 1999.99),
        ]
        
        for text, expected_amount in test_cases:
            words_result = [{'words': text, 'probability': {'average': 0.90}}]
            result = manager._parse_ocr_result(words_result, 'baidu')
            
            assert result is not None
            assert result['amount'] == expected_amount
    
    def test_parse_ocr_result_timestamp_with_slash(self, manager):
        """Test parsing timestamp with slash format"""
        words_result = [
            {'words': '时间: 2024/01/15 10:30', 'probability': {'average': 0.93}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        # Should convert slash to dash
        assert result['timestamp'] == '2024-01-15 10:30'
    
    def test_upload_proof_with_ocr_success(self, manager, app, monkeypatch):
        """Test upload includes OCR result when extraction succeeds"""
        with app.app_context():
            # Mock extract_payment_info to return a result
            mock_ocr_result = {
                'amount': 299.00,
                'transaction_id': '20240115123456789012',
                'timestamp': '2024-01-15 10:30:00',
                'confidence': 0.95,
                'ocr_provider': 'baidu',
                'extracted_at': '2024-01-15T10:31:00'
            }
            
            def mock_extract(file_path):
                return mock_ocr_result
            
            monkeypatch.setattr(manager, 'extract_payment_info', mock_extract)
            
            file = self.create_file_storage('test.jpg', b'test content', 'image/jpeg')
            order_id = 123
            
            result = manager.upload_proof(file, order_id)
            
            assert result['success'] is True
            assert 'ocr_result' in result
            assert result['ocr_result'] == mock_ocr_result
    
    def test_upload_proof_ocr_failure_silent(self, manager, app, monkeypatch):
        """Test upload succeeds even when OCR fails (silent failure)"""
        with app.app_context():
            # Mock extract_payment_info to raise an exception
            def mock_extract(file_path):
                raise Exception("OCR API failed")
            
            monkeypatch.setattr(manager, 'extract_payment_info', mock_extract)
            
            file = self.create_file_storage('test.jpg', b'test content', 'image/jpeg')
            order_id = 123
            
            result = manager.upload_proof(file, order_id)
            
            # Upload should still succeed
            assert result['success'] is True
            assert 'file_url' in result
            # OCR result should not be present
            assert 'ocr_result' not in result
    
    # Test OCR amount mismatch warning
    
    def test_ocr_amount_mismatch_detection(self, manager, app):
        """Test detection of amount mismatch between OCR and order"""
        with app.app_context():
            from app.models import Order
            
            # Create a test order with amount 299.00
            order = Order(
                order_no='TEST123',
                user_id=1,
                plan_id=1,
                amount=299.00,
                payment_status='pending'
            )
            
            # OCR extracted amount is different (399.00)
            ocr_result = {
                'amount': 399.00,
                'transaction_id': '20240115123456789012',
                'timestamp': '2024-01-15 10:30:00',
                'confidence': 0.95,
                'ocr_provider': 'baidu',
                'extracted_at': '2024-01-15T10:31:00'
            }
            
            # Check if amounts match (should not match)
            amount_diff = abs(order.amount - ocr_result['amount'])
            has_mismatch = amount_diff > 0.01
            
            assert has_mismatch is True
            assert amount_diff == 100.00
    
    def test_ocr_amount_match_no_warning(self, manager, app):
        """Test no warning when OCR amount matches order amount"""
        with app.app_context():
            from app.models import Order
            
            # Create a test order with amount 299.00
            order = Order(
                order_no='TEST123',
                user_id=1,
                plan_id=1,
                amount=299.00,
                payment_status='pending'
            )
            
            # OCR extracted amount matches
            ocr_result = {
                'amount': 299.00,
                'transaction_id': '20240115123456789012',
                'timestamp': '2024-01-15 10:30:00',
                'confidence': 0.95,
                'ocr_provider': 'baidu',
                'extracted_at': '2024-01-15T10:31:00'
            }
            
            # Check if amounts match (should match)
            amount_diff = abs(order.amount - ocr_result['amount'])
            has_mismatch = amount_diff > 0.01
            
            assert has_mismatch is False
            assert amount_diff == 0.00
    
    def test_ocr_amount_match_with_float_precision(self, manager, app):
        """Test amount matching considers floating point precision"""
        with app.app_context():
            from app.models import Order
            
            # Create a test order with amount 299.00
            order = Order(
                order_no='TEST123',
                user_id=1,
                plan_id=1,
                amount=299.00,
                payment_status='pending'
            )
            
            # OCR extracted amount has tiny difference due to float precision
            ocr_result = {
                'amount': 299.005,  # Within 0.01 tolerance
                'transaction_id': '20240115123456789012',
                'timestamp': '2024-01-15 10:30:00',
                'confidence': 0.95,
                'ocr_provider': 'baidu',
                'extracted_at': '2024-01-15T10:31:00'
            }
            
            # Check if amounts match (should match within tolerance)
            amount_diff = abs(order.amount - ocr_result['amount'])
            has_mismatch = amount_diff > 0.01
            
            assert has_mismatch is False
            assert amount_diff <= 0.01
    
    # Test low confidence handling
    
    def test_ocr_low_confidence_detection(self, manager):
        """Test detection of low confidence OCR results"""
        words_result = [
            {'words': '支付金额: ¥299.00', 'probability': {'average': 0.65}},
            {'words': '交易号: 20240115123456789012', 'probability': {'average': 0.60}},
            {'words': '支付时间: 2024-01-15 10:30:00', 'probability': {'average': 0.55}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        # Average confidence: (0.65 + 0.60 + 0.55) / 3 = 0.60
        assert result['confidence'] < 0.7
        assert 0.59 <= result['confidence'] <= 0.61
    
    def test_ocr_high_confidence(self, manager):
        """Test high confidence OCR results"""
        words_result = [
            {'words': '支付金额: ¥299.00', 'probability': {'average': 0.95}},
            {'words': '交易号: 20240115123456789012', 'probability': {'average': 0.92}},
            {'words': '支付时间: 2024-01-15 10:30:00', 'probability': {'average': 0.93}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        # Average confidence: (0.95 + 0.92 + 0.93) / 3 = 0.933
        assert result['confidence'] >= 0.7
        assert 0.93 <= result['confidence'] <= 0.94
    
    def test_ocr_mixed_confidence(self, manager):
        """Test OCR results with mixed confidence levels"""
        words_result = [
            {'words': '支付金额: ¥299.00', 'probability': {'average': 0.95}},
            {'words': '交易号: 20240115123456789012', 'probability': {'average': 0.50}},
            {'words': '其他文本', 'probability': {'average': 0.80}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        # Only matched fields contribute to confidence
        # Average: (0.95 + 0.50) / 2 = 0.725
        assert 0.70 <= result['confidence'] <= 0.75
    
    def test_ocr_confidence_without_probability(self, manager):
        """Test OCR results when probability field is missing (default 0.8)"""
        words_result = [
            {'words': '支付金额: ¥299.00'},  # No probability field
            {'words': '交易号: 20240115123456789012'}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        # Default confidence is 0.8 when probability is missing
        assert result['confidence'] == 0.8
    
    def test_upload_proof_with_low_confidence_ocr(self, manager, app, monkeypatch):
        """Test upload with low confidence OCR result"""
        with app.app_context():
            # Mock extract_payment_info to return low confidence result
            mock_ocr_result = {
                'amount': 299.00,
                'transaction_id': '20240115123456789012',
                'timestamp': '2024-01-15 10:30:00',
                'confidence': 0.55,  # Low confidence
                'ocr_provider': 'baidu',
                'extracted_at': '2024-01-15T10:31:00'
            }
            
            def mock_extract(file_path):
                return mock_ocr_result
            
            monkeypatch.setattr(manager, 'extract_payment_info', mock_extract)
            
            file = self.create_file_storage('test.jpg', b'test content', 'image/jpeg')
            order_id = 123
            
            result = manager.upload_proof(file, order_id)
            
            # Upload should succeed
            assert result['success'] is True
            # OCR result should be included even with low confidence
            assert 'ocr_result' in result
            assert result['ocr_result']['confidence'] < 0.7
    
    def test_ocr_partial_extraction_confidence(self, manager):
        """Test confidence calculation when only some fields are extracted"""
        words_result = [
            {'words': '支付金额: ¥299.00', 'probability': {'average': 0.95}},
            {'words': '其他无关文本', 'probability': {'average': 0.90}},
            {'words': '更多无关文本', 'probability': {'average': 0.85}}
        ]
        
        result = manager._parse_ocr_result(words_result, 'baidu')
        
        assert result is not None
        # Only amount was extracted, so confidence is based on that field only
        assert result['amount'] == 299.00
        assert result['transaction_id'] is None
        assert result['timestamp'] is None
        assert result['confidence'] == 0.95
