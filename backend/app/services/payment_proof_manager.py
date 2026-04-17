"""
支付凭证管理器 (PaymentProofManager)

处理支付凭证的上传、存储、验证和管理功能。
"""

import os
import base64
import requests
import json
from datetime import datetime
from typing import Tuple, Optional, Dict
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app


class PaymentProofManager:
    """支付凭证管理器"""
    
    # 支持的文件格式
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg',
        'image/jpg', 
        'image/png',
        'application/pdf'
    }
    
    # 文件大小限制 (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    def __init__(self):
        """初始化支付凭证管理器"""
        self.upload_base_path = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    def validate_file(self, file: FileStorage) -> Tuple[bool, str]:
        """
        验证文件格式和大小
        
        Args:
            file: 上传的文件对象
            
        Returns:
            (is_valid, error_message): 验证结果和错误信息
        """
        # 检查文件是否存在
        if not file or not file.filename:
            return False, "未选择文件"
        
        # 检查文件扩展名
        if not self._allowed_file(file.filename):
            return False, "不支持的文件格式，仅支持JPG、PNG、PDF"
        
        # 检查MIME类型
        if file.mimetype not in self.ALLOWED_MIME_TYPES:
            return False, f"不支持的文件类型: {file.mimetype}"
        
        # 检查文件大小
        # 先读取文件内容来检查大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        if file_size > self.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"文件大小超过5MB限制 (当前: {size_mb:.2f}MB)"
        
        if file_size == 0:
            return False, "文件为空"
        
        return True, ""
    
    def upload_proof(self, file: FileStorage, order_id: int) -> dict:
        """
        上传支付凭证
        
        Args:
            file: 上传的文件对象
            order_id: 订单ID
            
        Returns:
            {
                'success': bool,
                'file_url': str,
                'ocr_result': dict,  # 可选，OCR识别结果
                'error': str  # 可选，失败时返回
            }
        """
        # 验证文件
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            return {
                'success': False,
                'error': error_message
            }
        
        try:
            # 生成安全的文件名
            original_filename = file.filename
            file_ext = self._get_file_extension(original_filename)
            
            # 生成存储路径: uploads/payment_proofs/{year}/{month}/{order_id}_{timestamp}.{ext}
            now = datetime.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')
            timestamp = int(now.timestamp())
            
            # 构建目录路径
            dir_path = os.path.join(
                self.upload_base_path,
                'payment_proofs',
                year,
                month
            )
            
            # 确保目录存在
            os.makedirs(dir_path, exist_ok=True)
            
            # 生成文件名
            filename = f"{order_id}_{timestamp}.{file_ext}"
            file_path = os.path.join(dir_path, filename)
            
            # 保存文件
            file.save(file_path)
            
            # 生成相对URL路径
            file_url = f"/uploads/payment_proofs/{year}/{month}/{filename}"
            
            # 尝试OCR提取支付信息（静默失败）
            ocr_result = None
            try:
                ocr_result = self.extract_payment_info(file_path)
                current_app.logger.info(f"OCR提取成功: {ocr_result}")
            except Exception as e:
                # 静默失败，不影响上传
                current_app.logger.warning(f"OCR提取失败（静默失败）: {str(e)}")
            
            result = {
                'success': True,
                'file_url': file_url
            }
            
            if ocr_result:
                result['ocr_result'] = ocr_result
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"文件上传失败: {str(e)}")
            return {
                'success': False,
                'error': '文件上传失败，请稍后重试'
            }
    
    def get_proof_url(self, order_id: int) -> Optional[str]:
        """
        获取支付凭证URL
        
        Args:
            order_id: 订单ID
            
        Returns:
            支付凭证URL，如果不存在返回None
        """
        from app.models import Order
        
        order = Order.query.get(order_id)
        if order and order.payment_proof:
            return order.payment_proof
        return None
    
    def _allowed_file(self, filename: str) -> bool:
        """
        检查文件扩展名是否允许
        
        Args:
            filename: 文件名
            
        Returns:
            是否允许
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def _get_file_extension(self, filename: str) -> str:
        """
        获取文件扩展名
        
        Args:
            filename: 文件名
            
        Returns:
            文件扩展名（小写）
        """
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，确保安全
        
        Args:
            filename: 原始文件名
            
        Returns:
            安全的文件名
        """
        return secure_filename(filename)
    
    def extract_payment_info(self, file_path: str) -> Optional[Dict]:
        """
        使用OCR提取支付信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            {
                'amount': float,
                'transaction_id': str,
                'timestamp': str,
                'confidence': float,
                'ocr_provider': str,
                'extracted_at': str
            }
            如果提取失败返回None
        """
        provider = current_app.config.get('OCR_PROVIDER', 'baidu')
        
        try:
            if provider == 'baidu':
                return self._extract_with_baidu_ocr(file_path)
            elif provider == 'tencent':
                return self._extract_with_tencent_ocr(file_path)
            else:
                current_app.logger.error(f"不支持的OCR提供商: {provider}")
                return None
        except Exception as e:
            current_app.logger.error(f"OCR提取失败: {str(e)}")
            return None
    
    def _extract_with_baidu_ocr(self, file_path: str) -> Optional[Dict]:
        """
        使用百度OCR API提取支付信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的支付信息字典
        """
        api_key = current_app.config.get('BAIDU_OCR_API_KEY')
        secret_key = current_app.config.get('BAIDU_OCR_SECRET_KEY')
        
        if not api_key or not secret_key:
            current_app.logger.warning("百度OCR API密钥未配置")
            return None
        
        try:
            # 获取access_token
            token_url = "https://aip.baidubce.com/oauth/2.0/token"
            token_params = {
                'grant_type': 'client_credentials',
                'client_id': api_key,
                'client_secret': secret_key
            }
            token_response = requests.post(token_url, params=token_params, timeout=10)
            token_data = token_response.json()
            
            if 'access_token' not in token_data:
                current_app.logger.error(f"获取百度OCR token失败: {token_data}")
                return None
            
            access_token = token_data['access_token']
            
            # 读取图片并转换为base64
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 调用通用文字识别API
            ocr_url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
            ocr_data = {
                'image': image_data
            }
            ocr_response = requests.post(ocr_url, data=ocr_data, timeout=30)
            ocr_result = ocr_response.json()
            
            if 'words_result' not in ocr_result:
                current_app.logger.error(f"百度OCR识别失败: {ocr_result}")
                return None
            
            # 解析OCR结果
            return self._parse_ocr_result(ocr_result['words_result'], 'baidu')
            
        except Exception as e:
            current_app.logger.error(f"百度OCR调用失败: {str(e)}")
            return None
    
    def _extract_with_tencent_ocr(self, file_path: str) -> Optional[Dict]:
        """
        使用腾讯云OCR API提取支付信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的支付信息字典
        """
        secret_id = current_app.config.get('TENCENT_OCR_SECRET_ID')
        secret_key = current_app.config.get('TENCENT_OCR_SECRET_KEY')
        
        if not secret_id or not secret_key:
            current_app.logger.warning("腾讯云OCR API密钥未配置")
            return None
        
        try:
            # 腾讯云OCR需要使用SDK，这里简化处理
            # 实际生产环境应该使用腾讯云SDK
            current_app.logger.warning("腾讯云OCR暂未实现，请使用百度OCR")
            return None
            
        except Exception as e:
            current_app.logger.error(f"腾讯云OCR调用失败: {str(e)}")
            return None
    
    def _parse_ocr_result(self, words_result: list, provider: str) -> Optional[Dict]:
        """
        解析OCR识别结果，提取金额、交易流水号、时间戳
        
        Args:
            words_result: OCR识别的文字结果列表
            provider: OCR提供商
            
        Returns:
            解析后的支付信息
        """
        import re
        
        result = {
            'amount': None,
            'transaction_id': None,
            'timestamp': None,
            'confidence': 0.0,
            'ocr_provider': provider,
            'extracted_at': datetime.now().isoformat()
        }
        
        confidence_sum = 0.0
        confidence_count = 0
        
        # 遍历识别结果
        for item in words_result:
            text = item.get('words', '')
            item_confidence = item.get('probability', {}).get('average', 0.0) if 'probability' in item else 0.8
            
            # 提取金额（匹配模式：¥123.45, 123.45元, 金额:123.45）
            if not result['amount']:
                amount_patterns = [
                    r'¥\s*(\d+\.?\d*)',
                    r'(\d+\.?\d*)\s*元',
                    r'金额[：:]\s*(\d+\.?\d*)',
                    r'支付金额[：:]\s*(\d+\.?\d*)',
                    r'实付[：:]\s*(\d+\.?\d*)'
                ]
                for pattern in amount_patterns:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            result['amount'] = float(match.group(1))
                            confidence_sum += item_confidence
                            confidence_count += 1
                            break
                        except ValueError:
                            pass
            
            # 提取交易流水号（匹配模式：20-30位数字或字母数字组合）
            if not result['transaction_id']:
                transaction_patterns = [
                    r'流水号[：:]\s*([A-Za-z0-9]{15,30})',
                    r'交易号[：:]\s*([A-Za-z0-9]{15,30})',
                    r'订单号[：:]\s*([A-Za-z0-9]{15,30})',
                    r'([0-9]{20,30})'  # 纯数字流水号
                ]
                for pattern in transaction_patterns:
                    match = re.search(pattern, text)
                    if match:
                        result['transaction_id'] = match.group(1)
                        confidence_sum += item_confidence
                        confidence_count += 1
                        break
            
            # 提取时间戳（匹配模式：2024-01-15 10:30:00, 2024/01/15 10:30）
            if not result['timestamp']:
                timestamp_patterns = [
                    r'(\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2}:\d{2})',
                    r'(\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2})',
                    r'时间[：:]\s*(\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2})',
                    r'支付时间[：:]\s*(\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2})'
                ]
                for pattern in timestamp_patterns:
                    match = re.search(pattern, text)
                    if match:
                        result['timestamp'] = match.group(1).replace('/', '-')
                        confidence_sum += item_confidence
                        confidence_count += 1
                        break
        
        # 计算平均置信度
        if confidence_count > 0:
            result['confidence'] = confidence_sum / confidence_count
        
        # 如果没有提取到任何信息，返回None
        if not result['amount'] and not result['transaction_id'] and not result['timestamp']:
            return None
        
        return result
